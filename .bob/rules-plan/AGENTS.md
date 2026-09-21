# Project Architecture Rules (Non-Obvious Only)

- **The RAG layer is stateless and re-runs on every request.** `load_knowledge_base()` reads from disk and `retrieve_guidance_for_items()` scores from scratch each call — there is no caching. For scale, a cache would be needed, but this is a prototype.
- **AI and fallback paths share the same output schema.** Any change to the dict keys returned by `get_ai_recommendations()` must be reflected in both `_fallback_recommendations()` and `RESPONSE_SCHEMA_HINT` (the LLM schema instruction), and in the `app.py` rendering code — all three must stay in sync.
- **The LLM is constrained at the prompt level, not with structured output / tool-use features.** The model is told to return JSON via a plain text schema hint in `RESPONSE_SCHEMA_HINT`. If the model ignores this, `_extract_json()` catches it and `json.loads` will raise, which then triggers the fallback.
- **Knowledge-base retrieval is bounded.** `max_entries=6` prevents the prompt from growing unboundedly as the KB grows. If the KB grows significantly, revisit this cap to avoid silently dropping relevant entries.
- **Dual-layer empty-input protection:** `app.py` checks for empty items before calling the engine; the engine itself also handles an empty list safely. Both layers are intentional — do not remove either.
- **No persistence layer.** The app is fully stateless between page refreshes. No database, no session storage, no file writes during a session.
