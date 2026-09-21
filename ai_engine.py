"""
ai_engine.py
------------
Builds the prompt (grounded with retrieved knowledge-base guidance),
calls the LLM, and parses its structured output.

Also provides a transparent, rule-based fallback that runs automatically
if no API key is configured or the API call fails, so the demo never
just breaks. The UI always tells the user which mode produced the result.

LLM provider: Google Gemini API (google-genai SDK).
Required environment variable: GEMINI_API_KEY
Optional environment variable: GEMINI_MODEL (default: gemini-3.6-flash)

Important: GEMINI_MODEL is read lazily inside get_ai_recommendations() —
NOT at module import time — so that load_dotenv() in app.py has already
populated os.environ before the value is consumed.
"""

import json
import os
import re
from typing import List, Dict, Optional

from rag_engine import retrieve_guidance_for_items, format_guidance_for_prompt

# Default model name used when GEMINI_MODEL is not set in the environment.
# Read lazily inside get_ai_recommendations() so that load_dotenv() has
# already run before os.environ is consulted.
_DEFAULT_MODEL = "gemini-3.6-flash"

# The response schema instruction is part of the system prompt so the model
# sees it as a standing constraint, not just a per-turn request. This
# produces more consistent structured JSON output.
_RESPONSE_SCHEMA_HINT = """
You must respond with ONLY a single valid JSON object (no markdown fences,
no extra commentary before or after it) with exactly these keys:

{
  "use_first": [string, ...],
  "use_soon": [string, ...],
  "longer_storage": [string, ...],
  "leftover_ideas": [string, ...],
  "waste_reduction_actions": [string, ...],
  "shopping_planning_tip": string,
  "sustainability_impact": string,
  "safety_note": string
}

Rules for the content:
- "use_first", "use_soon", "longer_storage": short phrases referencing the
  user's actual items, based on whatever freshness/expiry/age information
  the user provided. If the user gave no freshness information for an item,
  say so plainly instead of guessing a specific shelf life.
- "leftover_ideas": concrete, practical reuse/repurposing ideas for the
  items provided. Each entry should be a short, actionable bullet phrase
  (one idea per string, not a multi-sentence paragraph).
- "waste_reduction_actions": simple, concrete actions the user can take
  this week.
- "shopping_planning_tip": one or two sentences on avoiding future
  over-purchasing, based on the pattern in this specific inventory.
- "sustainability_impact": one or two sentences, in general/qualitative
  terms (e.g. "reduces methane from food waste in landfills"), connecting
  the recommended actions to SDG 12. Do NOT invent specific numbers,
  percentages, or claims like "reduces waste by X%" -- no measurement has
  been taken.
- "safety_note": one or two sentences. Never invent exact expiry dates or
  state food-safety claims as certain fact. If safety is genuinely
  uncertain for any item, say so and recommend checking official/local
  food-safety guidance.
- Do not fabricate information the user did not provide (e.g. do not
  assume an exact purchase date if none was given).
"""

SYSTEM_PROMPT = (
    "You are a careful assistant embedded in a student sustainability "
    "project focused on SDG 12 (Responsible Consumption and Production). Your "
    "sole purpose is to help a user reduce avoidable food waste from the food "
    "items they list, by prioritizing consumption, suggesting reuse of "
    "leftovers, and giving simple waste-reduction and planning tips.\n\n"
    "You are NOT a general recipe chatbot and NOT a medical or food-safety "
    "authority. Follow these rules strictly:\n"
    "- Base freshness/priority judgments only on information the user actually "
    "provided (quantity, approximate age, expiry info). Never invent exact "
    "expiry dates or specific shelf-life numbers that were not given or that "
    "are not general common knowledge.\n"
    "- Never present uncertain food-safety information as settled fact. Where "
    "there is real uncertainty, say so and recommend checking official or "
    "local food-safety guidance.\n"
    "- Clearly keep your suggestions grounded in the user's actual inventory -- "
    "do not assume items the user did not list.\n"
    "- Do not fabricate statistics, studies, or specific quantitative impact "
    "claims (e.g. never say \"this reduces waste by 40%\"). Impact statements "
    "must stay qualitative/expected, not measured.\n"
    "- You may use the \"curated guidance\" provided to you as background "
    "knowledge, but you still must reason about the user's specific items.\n"
    + _RESPONSE_SCHEMA_HINT
)


def build_user_prompt(
    items: List[Dict], num_people: Optional[int], retrieved_guidance: List[Dict]
) -> str:
    lines = ["The user has the following food inventory:"]
    for it in items:
        parts = [f"- {it['name']}"]
        if it.get("quantity"):
            parts.append(f"(quantity: {it['quantity']})")
        if it.get("age_or_freshness"):
            parts.append(f"(freshness/age noted by user: {it['age_or_freshness']})")
        if it.get("expiry"):
            parts.append(f"(expiry info noted by user: {it['expiry']})")
        lines.append(" ".join(parts))

    if num_people:
        lines.append(f"\nApproximate number of people eating: {num_people}")
    else:
        lines.append("\nNumber of people eating was not provided.")

    lines.append("\nCurated background guidance retrieved for these items (use as helpful context, not as absolute fact for items it doesn't mention):")
    lines.append(format_guidance_for_prompt(retrieved_guidance))

    # The schema hint is already in the system prompt; the user turn carries
    # only the inventory data and retrieved guidance.
    return "\n".join(lines)


def _extract_json(text: str) -> Dict:
    """Best-effort extraction of a JSON object from the model's text output.

    Handles:
    - bare JSON (the expected case)
    - ```json ... ``` or ``` ... ``` fences (model ignored instructions)
    - leading/trailing prose around the JSON object
    """
    text = text.strip()
    # Remove any opening code fence on its own line (with or without "json" tag).
    text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.IGNORECASE)
    # Remove any closing code fence on its own line.
    text = re.sub(r"\n?```\s*$", "", text, flags=re.IGNORECASE)
    text = text.strip()
    # Extract the outermost JSON object in case there is surrounding prose.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def get_ai_recommendations(
    items: List[Dict], num_people: Optional[int]
) -> Dict:
    """
    Attempts an LLM call grounded with retrieved knowledge-base guidance.
    Returns a dict with a "mode" key ("ai" or "fallback") so the UI can be
    transparent about which path produced the result, plus the
    recommendation fields described in _RESPONSE_SCHEMA_HINT / SYSTEM_PROMPT.

    Uses the Google Gemini API (google-genai SDK).
    Reads GEMINI_API_KEY and GEMINI_MODEL from the environment at call time
    (not at import time) so that .env values loaded by load_dotenv() are
    always visible.
    """
    from rag_engine import load_knowledge_base

    # Resolve model name here, not at module level, so the value from .env
    # is always available (load_dotenv() runs in app.py before this is called).
    model_name = os.environ.get("GEMINI_MODEL", _DEFAULT_MODEL)

    item_names = [it["name"] for it in items]
    kb = load_knowledge_base()
    retrieved = retrieve_guidance_for_items(item_names, kb)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return _fallback_recommendations(items, retrieved, reason="No GEMINI_API_KEY configured.")

    try:
        import logging
        import google.genai as genai
        from google.genai import types as genai_types

        # Suppress the SDK's informational AFC warning (we don't use function
        # calling; the warning is cosmetic and not an error).
        logging.getLogger("google.genai").setLevel(logging.ERROR)

        client = genai.Client(api_key=api_key)
        user_prompt = build_user_prompt(items, num_people, retrieved)

        response = client.models.generate_content(
            model=model_name,
            contents=user_prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=1800,
                # Request JSON output directly; the schema hint in SYSTEM_PROMPT
                # already specifies the exact structure the model must return.
                response_mime_type="application/json",
                # Disable automatic function calling — this app doesn't use tools.
                automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )
        raw_text = response.text or ""
        parsed = _extract_json(raw_text)
        parsed["mode"] = "ai"
        parsed["retrieved_guidance_used"] = [e["id"] for e in retrieved]
        return parsed

    except Exception as e:  # noqa: BLE001 -- broad on purpose: any failure -> fallback
        result = _fallback_recommendations(items, retrieved, reason=str(e))
        return result


def _fallback_recommendations(
    items: List[Dict], retrieved: List[Dict], reason: str
) -> Dict:
    """
    A transparent, deterministic, rule-based fallback used only when the
    AI call is unavailable or fails, so the app remains demoable offline
    or without an API key. This is intentionally simple and rule-based --
    it is NOT presented as AI-generated output.
    """
    use_first, use_soon, longer_storage = [], [], []

    # Words that indicate a COOKED or perishable item (substring match on item name).
    # Plain "rice" is intentionally absent — uncooked rice is durable.
    # "cooked rice", "leftover rice" etc. still match via "cooked" / "leftover".
    perishable_hint_words = ["cooked", "leftover", "curry", "dal", "milk", "curd", "bread"]
    # Words that indicate a DRY / durable staple. "rice" here catches plain
    # "Rice", "rice (1 kg)", "uncooked rice", etc.
    durable_hint_words = ["rice", "potato", "onion", "dry", "flour", "lentil"]

    for it in items:
        name = it["name"]
        age = (it.get("age_or_freshness") or "").lower()
        expiry = (it.get("expiry") or "").lower()

        flagged_urgent = any(
            w in age for w in ["yesterday", "2 day", "two day", "old", "3 day", "expiring", "soon"]
        ) or any(w in expiry for w in ["today", "tomorrow", "expiring", "expired"])

        if flagged_urgent:
            use_first.append(name)
        elif any(w in name.lower() for w in perishable_hint_words):
            use_soon.append(name)
        elif any(w in name.lower() for w in durable_hint_words):
            longer_storage.append(name)
        else:
            use_soon.append(name)

    # Build concise, bullet-style leftover ideas from matched KB entries rather
    # than returning multi-sentence guidance paragraphs verbatim.
    _leftover_summaries = {
        "leftovers_general": "Use a first-in-first-out approach: store leftovers in clear containers at the front of the fridge so they aren't forgotten.",
        "cooked_legumes": "Repurpose leftover dal/curry into parathas, cutlets, soup, or a wrap filling instead of reheating the same dish repeatedly.",
        "cooked_grains": "Leftover cooked rice is best used within 1–2 days; try it as fried rice or add it to a soup.",
        "bread": "Stale (but not mouldy) bread works well for toast, croutons, or bread pudding; freeze it if you won't use it soon.",
    }
    leftover_ideas = [
        _leftover_summaries[e["id"]]
        for e in retrieved
        if e["id"] in _leftover_summaries
    ]
    if not leftover_ideas:
        leftover_ideas = ["Combine small leftover quantities into a single mixed dish rather than discarding them separately."]

    waste_actions = [
        "Store perishable items visibly in the fridge (not at the back) so they aren't forgotten.",
        "Cook or use items flagged 'Use first' before starting anything new.",
    ]

    return {
        "mode": "fallback",
        "fallback_reason": reason,
        "use_first": use_first,
        "use_soon": use_soon,
        "longer_storage": longer_storage,
        "leftover_ideas": leftover_ideas,
        "waste_reduction_actions": waste_actions,
        "shopping_planning_tip": "Check what you already have before your next shopping trip, and buy perishable items in smaller, more frequent quantities.",
        "sustainability_impact": "Prioritizing items that are closer to spoiling and reusing leftovers can help reduce avoidable household food waste, which in turn reduces the resources and emissions associated with wasted food.",
        "safety_note": "This fallback mode uses simple rules, not an AI model, because no AI response was available. It does not know your food's actual condition -- use your own judgement and check official food-safety guidance if you are unsure whether something is still good to eat.",
        "retrieved_guidance_used": [e["id"] for e in retrieved],
    }
