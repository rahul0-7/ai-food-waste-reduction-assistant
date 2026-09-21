# Project Coding Rules (Non-Obvious Only)

- **Never let `get_ai_recommendations()` raise.** The broad `except Exception` in `ai_engine.py` is intentional — always route failures to `_fallback_recommendations()` and set `"mode": "fallback"`.
- **`_extract_json()` must stay defensive.** The model is instructed to return bare JSON, but the regex fence-stripping is the safety net — don't remove it.
- **Fallback hard-codes knowledge-base IDs.** `_fallback_recommendations()` filters retrieved guidance by `entry["id"]` — if you rename any `knowledge_base.json` IDs, update that filter list too.
- **`load_knowledge_base()` is called inside `get_ai_recommendations()` (not at module import time)** to avoid file I/O on import. Keep it that way.
- **RAG is keyword-only, intentionally.** Do not add embedding or vector-search approaches without updating `DOCUMENTATION.md`'s "Limitations" section — the simplicity is a documented design choice.
- **`"mode"` key is always required in the returned dict** — the UI branches on `result.get("mode") == "ai"`. Any new code path returning a dict must include it.
- All UI sections (Use First / Use Soon / Longer Storage / leftover_ideas / etc.) guard against `None` with `or []` / `or ""` — maintain this pattern for new fields.
- The `ANTHROPIC_API_KEY` env var is the only required secret; it is loaded via `python-dotenv` in `app.py`. Do not add new secrets without updating `.env.example`.
