"""
rag_engine.py
--------------
A deliberately simple Retrieval-Augmented Generation (RAG) step.

Why simple keyword matching instead of embeddings/a vector database?
This is a short-timeline student prototype. A lightweight, explainable
retrieval method keeps the project easy to demo, easy to explain to a
non-technical evaluator, and easy to run with no extra infrastructure
(no vector DB, no embedding API calls, no GPU). The trade-off is that it
is less semantically flexible than embedding-based retrieval -- that is
called out explicitly in the documentation's "Limitations" section
rather than hidden.

How it works:
1. Each knowledge-base entry has a list of keywords.
2. For every food item the user enters, we score each knowledge-base
   entry by counting how many of its keywords appear in the item name
   (simple substring matching, case-insensitive).
3. The highest-scoring entries (score > 0) are retrieved and passed to
   the LLM as grounding context, so the model's suggestions are based on
   curated guidance rather than purely on its own unguided generation.
"""

import json
import os
from typing import List, Dict


def load_knowledge_base(path: str = None) -> List[Dict]:
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _score_entry(item_name: str, entry: Dict) -> int:
    item_lower = item_name.lower()
    score = 0
    for kw in entry.get("keywords", []):
        if kw.lower() in item_lower:
            score += 1
    return score


def retrieve_guidance_for_items(
    item_names: List[str], knowledge_base: List[Dict], max_entries: int = 6
) -> List[Dict]:
    """
    Returns the most relevant knowledge-base entries (deduplicated) for a
    list of food item names, ranked by total keyword-match score across
    all items. Only entries with a positive score are returned.
    """
    scored = {}
    for item_name in item_names:
        for entry in knowledge_base:
            score = _score_entry(item_name, entry)
            if score > 0:
                key = entry["id"]
                if key not in scored or score > scored[key][0]:
                    scored[key] = (score, entry)

    ranked = sorted(scored.values(), key=lambda x: x[0], reverse=True)
    return [entry for _, entry in ranked[:max_entries]]


def format_guidance_for_prompt(entries: List[Dict]) -> str:
    if not entries:
        return "No specific curated guidance matched these items; rely on general, cautious food-waste-reduction knowledge."
    lines = []
    for entry in entries:
        lines.append(f"- {entry['guidance']}")
    return "\n".join(lines)
