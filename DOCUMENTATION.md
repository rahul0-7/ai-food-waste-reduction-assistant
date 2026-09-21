# Project Documentation

**1M1B AI for Sustainability Virtual Internship (July–September 2026)**

A note on accuracy: this document only states things that are true of what was actually built,
or clearly marks a section as a template for you to personalize. It does not include invented
statistics, fabricated user studies, or made-up test results.

---

## 1. Project Title

**AI Food Waste Reduction Assistant**

---

## 2. Problem Statement

> "How might we use AI to help individuals reduce avoidable food waste by making better decisions
> about consuming, reusing, storing and planning food?"

(Used as given in the brief — it already captures the core scope clearly.)

---

## 3. SDG Alignment

**Primary SDG: SDG 12 — Responsible Consumption and Production.**

SDG 12 specifically calls for reducing food waste and using resources more responsibly across
the consumption chain. This project targets the household/individual and small-institution
(hostel, mess, canteen) end of that chain, where day-to-day decisions — not industrial-scale
supply chain issues — are the main driver of avoidable waste.

---

## 4. Target Users

- Students living in hostels or PGs who cook for themselves or share a mess.
- Households that want to reduce food spoilage and grocery overspending.
- College canteens/mess managers looking for a simple, low-effort planning aid.

---

## 5. Problem Background

Food is unnecessarily wasted in households, hostels, college messes and canteens for a
combination of everyday reasons: people buy or prepare more than they need, forget what they
already have in the fridge or pantry, don't have a simple way to know what should be eaten
first, and don't know how to creatively reuse leftovers before they spoil. None of these causes
require expensive infrastructure to address — they are largely decision-support problems, which
is what makes a lightweight AI assistant a reasonable fit.

---

## 6. Proposed Solution

A web app where a user lists their current food items (optionally with quantity, freshness/age,
and expiry information). The system analyzes this inventory and returns:

- **Use First** — items to prioritize based on what the user told it about freshness/age.
- **Use Soon** — items to consume in the near term.
- **Longer Storage** — items that can generally wait.
- **Leftover / Reuse Ideas** — practical ways to use what's already there.
- **Waste-Reduction Actions** — small, concrete habits.
- **Shopping/Planning Tip** — how to avoid over-buying next time.
- **Sustainability Impact** — a qualitative, expected (not measured) connection to SDG 12.
- **Safety Note** — an explicit reminder of the limits of the tool and when to check official
  food-safety guidance.

---

## 7. Why AI is Needed

A fixed rule ("rice lasts 2 days, tomatoes last 5 days") cannot handle the huge variety of
real-world inventories, mixed cuisines, and free-text ways people describe their food ("half a
loaf," "cooked yesterday," "a bit soft"). An LLM can read unstructured, natural descriptions of
a real inventory and reason about relative priority and reuse ideas across many different item
types at once — while a small set of hard-coded rules would either be too rigid or would require
covering an unrealistic number of specific foods by hand. AI is used here for *reasoning and
language understanding over messy, varied input*, not for anything that requires model training.

---

## 8. AI Components / Tools Used

- **LLM:** Google Gemini, called via the official `google-genai` SDK directly from the
  Streamlit backend. Model: `gemini-3.6-flash` (the default). The model can be overridden
  without changing code by setting the `GEMINI_MODEL` environment variable in `.env`.
  The required secret is `GEMINI_API_KEY` (obtained free from Google AI Studio).
- **Prompt engineering:** a system prompt constrains the model's behavior (grounded reasoning
  only from user-supplied details; no invented expiry dates; no unqualified food-safety claims;
  no fabricated quantitative impact numbers; structured JSON output).
- **Structured JSON output:** the Gemini API is called with `response_mime_type="application/json"`
  and `_extract_json()` defensively strips any stray markdown fences before parsing, ensuring the
  UI always receives a well-formed response dict.
- **Lightweight RAG (Retrieval-Augmented Generation):** a small, hand-curated knowledge base
  (`knowledge_base.json`, ~16 entries of general food-storage/waste guidance) is searched with
  simple keyword matching for each user-entered item, and the matched guidance is inserted into
  the prompt as grounding context before the model answers. No vector database is required.
- **Deterministic rule-based fallback:** used only if `GEMINI_API_KEY` is not configured or the
  Gemini API call fails for any reason, so the demo does not break; clearly labelled as non-AI
  when shown.

---

## 9. System Workflow

1. User enters food items (+ optional quantity/freshness/expiry) and optional headcount in the
   Streamlit UI.
2. On "Analyze," the backend retrieves relevant curated guidance for the entered items
   (`rag_engine.py`).
3. The backend builds a prompt combining the user's inventory, the retrieved guidance, and
   strict output/behavior instructions, and sends it to the Google Gemini API (`ai_engine.py`).
4. Gemini returns a structured JSON response, which is parsed and displayed as prioritized
   categories, reuse ideas, actions, a planning tip, an impact statement, and a safety note.
5. If the Gemini API is unavailable, a rule-based fallback produces an analogous (clearly
   labelled) result instead so the UI is never left broken.

---

## 10. Prototype Description

A working Streamlit web app (`app.py`) with:
- An editable table for entering food items (add/remove rows), pre-filled with the example from
  the brief.
- An "Analyze" button that runs the pipeline above and displays results in labelled sections.
- Expandable sections explaining the problem, Responsible AI notice, and project/SDG background,
  so it is easy to explain to a non-technical evaluator without leaving the app.
- A visible banner stating whether a given result came from the AI model or the rule-based
  fallback (transparency).

The app runs with Google Gemini when `GEMINI_API_KEY` is configured, and automatically falls
back to the clearly-labelled rule-based mode when the Gemini API is unavailable. It is ready
to run locally with `streamlit run app.py` or to deploy to Streamlit Community Cloud (see
`README.md`).

---

## 11. IBM Bob Integration

[IBM Bob](https://www.ibm.com/bob) is an AI-powered development assistant. It was used
throughout the development of this project as a hands-on development partner, not just for
information lookup.

**Activities performed with IBM Bob:**

- **Project initialization and codebase analysis** — the `/init` command was run to let Bob
  read and analyse the full project; Bob identified the module structure, the data-flow path
  (`app.py → ai_engine.py → rag_engine.py → knowledge_base.json`), and the coding conventions
  used across the project, establishing shared context for all subsequent work.
- **Architecture and code review** — Bob reviewed `ai_engine.py`, `rag_engine.py`, and `app.py`,
  identified implementation issues, and confirmed which parts of the code were working as intended.
- **LLM migration (Anthropic → Google Gemini)** — Bob assisted in migrating the LLM integration
  from the Anthropic Claude API to the Google Gemini API (`google-genai` SDK), updating prompt
  construction, the API call, and JSON response-parsing logic in `ai_engine.py`.
- **Environment variable and model configuration** — Bob helped configure `GEMINI_API_KEY` and
  the optional `GEMINI_MODEL` override, and updated `.env.example` accordingly.
- **Debugging the model-loading issue** — Bob diagnosed a bug where `MODEL_NAME` in
  `ai_engine.py` was evaluated at module import time, before `load_dotenv()` ran in `app.py`,
  causing the `GEMINI_MODEL` value from `.env` to be silently ignored. The fix moved
  `load_dotenv()` before the `ai_engine` import in `app.py` and changed model resolution to a
  lazy read inside `get_ai_recommendations()`.
- **Fallback logic and JSON handling improvements** — Bob reviewed and helped improve the
  `_fallback_recommendations()` function and the defensive `_extract_json()` parser.
- **Regression testing** — Bob helped write and verify `test_model_name.py`, a four-case test
  suite confirming that the correct Gemini model name is sent to the API under all relevant
  conditions (default value, env-var override, simulated `load_dotenv()`, and regression against
  the old `gemini-2.5-flash` default).
- **Verification of the working Gemini integration** — Bob helped verify the end-to-end Gemini
  integration, confirming that a real `GEMINI_API_KEY` produces AI-generated recommendations and
  that the fallback path activates cleanly when the API is unavailable.

---

## 12. Responsible AI Considerations

- **Fairness:** The tool applies the same reasoning process to every user's inventory and does
  not use or ask for any personal/demographic attributes.
- **Transparency:** Results are explicitly labelled as AI-generated or rule-based fallback. The
  UI states plainly that the tool is reasoning from user-provided text, not from any actual
  inspection of the food.
- **Ethics:** The system prompt explicitly forbids inventing exact expiry dates, presenting
  uncertain food-safety claims as fact, or fabricating quantitative impact numbers. The UI carries
  a persistent Responsible AI notice and a safety note is shown with every result.
- **Privacy:** Only food-related details are collected. No names, contacts, location, or other
  personal data are requested, stored, or required for the tool to function.

---

## 13. Expected Impact

Framed as *expected*, not measured (no user study has been run):

- **Social:** Individuals and hostel/mess residents get a quick way to decide what to cook next
  and how to use leftovers, potentially reducing thrown-away food and grocery spend.
- **Environmental:** Less food waste means less avoidable use of the water, land, and energy that
  went into producing that food, and less organic waste sent to landfill (where it produces
  methane as it decomposes).
- **Economic:** Reduced over-purchasing and reduced spoilage can lower a household's or mess's
  grocery costs over time.

No specific percentage or quantitative reduction is claimed anywhere in this project, because no
measurement study has actually been conducted.

---

## 14. Limitations

- The AI has no way to verify the actual physical condition of any food item — it only reasons
  from what the user types.
- The knowledge base is small and keyword-matched rather than using semantic/embedding-based
  retrieval, so it will sometimes miss relevant guidance for items phrased unusually or not
  covered by its ~16 entries.
- The tool is not a food-safety authority and should not be used as the sole basis for a genuinely
  uncertain safety decision.
- No user study or real-world deployment has been conducted; impact is expected/qualitative, not
  measured.
- The rule-based fallback is intentionally simple and less capable than the AI mode.

---

## 15. Future Scope

- Expand the knowledge base and move to embedding-based retrieval for better matching on
  unusual phrasing.
- Add optional photo-based input (e.g. a fridge photo) if a vision-capable pipeline is added later.
- Add simple local storage of a user's inventory across sessions (with clear consent), to track
  what's been used over time.
- Partner with a real hostel/mess to pilot the tool and gather actual (not assumed) feedback,
  which could later support a genuine impact measurement.

---

## 16. Testing / Sample Inputs and Outputs

See `SAMPLE_TEST_INPUTS.md` for the full set of test cases. Summary of what was verified:

- **Live Gemini API (AI mode):** tested end-to-end with a real `GEMINI_API_KEY`. The app
  successfully produced AI-generated recommendations and displayed the banner:
  *"Suggestions generated by the AI model, grounded with curated food-waste guidance."*
  The example inventory from the brief (2 tomatoes, half a loaf of bread, cooked dal from
  yesterday, 1 kg rice) produced a labelled result for every output category, with cooked dal
  and bread correctly prioritized ahead of uncooked rice.
- **Rule-based fallback:** verified that when the Gemini API returned a temporary 503 error,
  the app automatically fell back to the rule-based path and displayed the on-screen fallback
  notice rather than crashing or showing an unhandled error.
- **Empty-input guard:** submitting with no items entered shows a clear warning instead of
  erroring (verified via the empty-input check in `app.py`).
- **Model-selection regression tests:** `test_model_name.py` (four cases) confirms that
  `gemini-3.6-flash` is the model name sent to the Gemini API under all conditions — default
  (no env var), `GEMINI_MODEL` env-var override, simulated `load_dotenv()`, and regression
  against the old `gemini-2.5-flash` default. All four tests pass.
- **Syntax / import check:** `app.py`, `ai_engine.py`, and `rag_engine.py` all import and
  initialize cleanly with `streamlit run app.py`.

---

## 17. Short Project Story

Food waste rarely happens because someone doesn't care — it happens because remembering what's
in the fridge, and what to cook with it, is a small but constant mental load. This project asks
a narrow, practical question: if someone just types out what they currently have, can an AI
assistant turn that into a short, prioritized set of suggestions that makes it a little easier to
use food before it spoils? The prototype here answers that question directly, while being upfront
about what it doesn't know (the food's actual condition) and what it can't yet prove
(measured impact).

---

## 18. How the Internship Helped Me Build This Project

Before this internship, I knew how to write code, but I had not thought carefully about
connecting an AI project to a real-world sustainability goal. The program's framing around
SDG 12 pushed me to start with the problem — unnecessary household food waste — rather than
with the technology, and that shaped every design decision that followed.

The emphasis on responsible AI in the program directly influenced how I built this prototype.
I added explicit constraints to the system prompt, a visible fallback banner, and a safety note
with every result — not as afterthoughts, but because the internship made clear that an AI
system's trustworthiness matters as much as its outputs.

On the technical side, working with Google Gemini, a lightweight RAG pipeline, Streamlit, and
IBM Bob taught me what end-to-end AI development actually looks like in practice. Debugging the
environment-variable loading issue and verifying the fallback behavior under a real API error
were more instructive than any clean tutorial scenario — they showed me that production-readiness
is about handling failure gracefully, not just making the happy path work.
