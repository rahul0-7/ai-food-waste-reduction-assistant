# Project Documentation Context (Non-Obvious Only)

- **`DOCUMENTATION.md`** is the full project write-up (design thinking, limitations, responsible-AI section). It is the canonical reference for design intent — not the README.
- **`SAMPLE_TEST_INPUTS.md`** contains real verified outputs from the fallback path (no API key was available when it was written). These are the actual test cases, not illustrative examples.
- **`PRESENTATION_SCRIPT.md`** and **`SUBMISSION_CHECKLIST.md`** are internship-submission artefacts — do not treat them as functional code documentation.
- **Section 11 of `DOCUMENTATION.md`** ("IBM BOB Integration") is intentionally left as a placeholder — it was not filled in because the definition of "IBM BOB" in this program context was unclear. Do not invent content for it.
- **The "fallback" mode is a first-class feature**, not an error state. It is explicitly documented in the UI and in `SAMPLE_TEST_INPUTS.md`. Questions about "why is it not using AI" should start with whether `ANTHROPIC_API_KEY` is set.
- **No automated tests exist.** All testing is manual, driven by the sample inputs in `SAMPLE_TEST_INPUTS.md`. There is no pytest, unittest, or any test directory.
