# Submission Checklist

## Before you submit / present

- [ ] Get an Anthropic API key from https://console.anthropic.com/ and add it to `.env`
      (locally) and/or Streamlit Community Cloud secrets (for deployment).
- [ ] Run `pip install -r requirements.txt` and confirm `streamlit run app.py` works locally.
- [ ] Test all four sample cases in `SAMPLE_TEST_INPUTS.md` **with your real API key**, so you
      see genuine AI-generated output at least once before presenting (this build environment
      only verified the rule-based fallback path — see README for why).
- [ ] Deploy to Streamlit Community Cloud (or your chosen host) and confirm the public link works.
- [ ] Fill in **Section 11 (IBM BOB Integration)** and **Section 18 (How the internship helped
      me)** in `DOCUMENTATION.md` — both are intentionally left for you, see the notes there.
- [ ] Read through `DOCUMENTATION.md` once fully and adjust anything that should reflect your own
      voice/experience rather than the draft wording.
- [ ] Time yourself reading `PRESENTATION_SCRIPT.md` out loud and trim/adjust to fit your actual
      time limit and speaking style.

## Screenshots to take (for your submission package)

1. The full app homepage (problem explanation + input table visible).
2. The Responsible AI notice expanded.
3. A filled-in inventory table (e.g. Case 1 from `SAMPLE_TEST_INPUTS.md`) right before clicking
   Analyze.
4. The results screen after clicking Analyze, with the "AI-generated" banner visible (not the
   fallback banner — make sure your API key is working before taking this one).
5. The "About this project / SDG 12 alignment" section expanded.
6. (Optional) Your deployed Streamlit Community Cloud app settings page showing it's live, with
   the secret redacted/blurred.

## Suggested submission package contents

- [ ] Link to your deployed app (Streamlit Community Cloud URL).
- [ ] Link to your GitHub repository (with `.env` excluded via `.gitignore`).
- [ ] `DOCUMENTATION.md` (completed, including Sections 11 and 18).
- [ ] Screenshots (above).
- [ ] `PRESENTATION_SCRIPT.md` (adjusted to your voice) for your live/recorded presentation.
- [ ] `SAMPLE_TEST_INPUTS.md` with your own screenshots/notes of the AI-mode output added.

## Things this project intentionally does NOT claim (keep it this way in your submission)

- No claim that the system solves food waste globally.
- No fabricated percentage, statistic, or "our testing showed X% reduction" claim of any kind —
  only qualitative, expected impact statements.
- No claim of a completed user study — none was run.
- No exact expiry dates invented by the AI for items the user didn't give dates for.
