# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack

- **Python 3.9+**, Streamlit UI, Anthropic Claude API, no test framework, no linter config.
- Only 4 runtime dependencies: `streamlit`, `pandas`, `python-dotenv`, `anthropic` (see `requirements.txt`).

## Run / Build

```bash
streamlit run app.py           # starts app at http://localhost:8501
pip install -r requirements.txt
```

No build step. No `package.json`. No `Makefile`. No test runner command — testing is manual via the browser using `SAMPLE_TEST_INPUTS.md`.

## Environment

- Requires `.env` file (copy from `.env.example`) with `ANTHROPIC_API_KEY=sk-ant-...`.
- App **intentionally runs without an API key** — it falls back to a deterministic rule-based path and labels the output as "fallback" on-screen. Never add a guard that prevents startup without the key.

## Architecture (3 files + 1 JSON)

```
app.py  →  ai_engine.get_ai_recommendations()  →  rag_engine.retrieve_guidance_for_items()
                                                →  knowledge_base.json  (RAG source, hand-curated)
```

- `app.py` — Streamlit UI only; no business logic.
- `ai_engine.py` — prompt building (`build_user_prompt`), LLM call, JSON parsing (`_extract_json`), and `_fallback_recommendations`.
- `rag_engine.py` — simple keyword-match retrieval over `knowledge_base.json`; no embeddings, no vector DB.
- `knowledge_base.json` — list of objects, each with `"id"`, `"keywords"` (list), and `"guidance"` (string).

## Critical Patterns

- **LLM model:** `MODEL_NAME = "claude-sonnet-5"` in `ai_engine.py`. Cheaper swap during testing: `"claude-haiku-4-5-20251001"`.
- **LLM output is raw JSON** (no markdown fences — the prompt explicitly forbids them). `_extract_json()` defensively strips fences anyway with regex before `json.loads`.
- **`get_ai_recommendations()` always returns a dict** with a `"mode"` key (`"ai"` or `"fallback"`). Never let it raise — the `except Exception` catch is intentional (`# noqa: BLE001`).
- **Fallback perishable/durable keyword lists** live directly in `_fallback_recommendations()` — update them there when adding new food categories.
- **RAG retrieval cap:** `max_entries=6` in `retrieve_guidance_for_items()`. Entries are deduplicated by `entry["id"]`; highest score wins when the same entry matches multiple items.

## Code Style (observed conventions)

- Module-level docstrings on every `.py` file explaining purpose and design rationale.
- Type hints on all function signatures (`List[Dict]`, `Optional[int]`, etc.) using `typing` imports.
- UI copy uses `st.markdown`, `st.success`, `st.warning`, `st.info` — never `st.write` for styled output.
- Constants (`MODEL_NAME`, `RESPONSE_SCHEMA_HINT`, `SYSTEM_PROMPT`) defined at module top, not inline.
- Imports: stdlib first, then third-party (`streamlit`, `pandas`, `anthropic`), then local (`from ai_engine import ...`). Local imports inside functions are used only when avoiding circular imports (e.g., `from rag_engine import load_knowledge_base` inside `get_ai_recommendations`).

## Knowledge Base

- To add a new food category: append a JSON object to `knowledge_base.json` with unique `"id"`, relevant `"keywords"`, and a `"guidance"` string.
- The fallback path in `ai_engine._fallback_recommendations()` hard-codes some `entry["id"]` values (`"leftovers_general"`, `"cooked_legumes"`, etc.) — update that list if you rename IDs.
