# Sample Test Inputs

These are ready-to-use inputs for demoing or testing the app. The outputs shown for Cases 1–3
below are **real, verified outputs from this build environment** — they came from the rule-based
fallback path (`ai_engine.py`), because no `ANTHROPIC_API_KEY` was available in this sandbox to
call the live model. They are included so you have honest, actually-tested reference output, not
invented examples. **Before your demo, re-run these same inputs with a real API key** to see (and
optionally screenshot) the AI-generated version, which will typically be more nuanced in its
wording than the fallback.

---

## Case 1 — The brief's example inventory

**Input** (already pre-filled as the app's default rows):

| Item | Quantity | Freshness / Age | Expiry info |
|---|---|---|---|
| Tomatoes | 2 | | |
| Bread | half loaf | a few days old | |
| Cooked dal | | cooked yesterday | |
| Rice | 1 kg | uncooked | |

**People:** 3

**Verified fallback output (real, from this build):**
- Use First: Bread, Cooked dal
- Use Soon: Tomatoes, Rice
- Longer Storage: (none flagged)
- Leftover ideas: reuse suggestions for the dal (parathas/cutlets/wraps) and the bread (toast/
  croutons/bread pudding, freeze if not needed soon), plus a note about rice food-safety practice.
- Shopping tip, sustainability impact, and safety note all populated (see README's "Where the AI
  is used" section for what these mean).

**What to check when you re-run this with a real API key:** the AI version should give similarly
structured but more specific reasoning (e.g. noting the dal is a day old so it's flagged first),
and should still show the safety note.

---

## Case 2 — Near-expiry / edge-case dairy

**Input:**

| Item | Quantity | Freshness / Age | Expiry info |
|---|---|---|---|
| Milk | 500 ml | opened 2 days ago | expiring tomorrow |
| Onions | 3 | | |

**Verified fallback output (real, from this build):**
- Use First: Milk
- Longer Storage: Onions
- Retrieved guidance used: dairy handling guidance, root-vegetable storage guidance.

**What this tests:** that explicit "expiring tomorrow" language correctly triggers "Use First,"
and that a durable item (onions) with no freshness info is correctly treated as lower priority.

---

## Case 3 — Empty input (error handling)

**Input:** no rows filled in, click Analyze.

**Verified behavior:** `app.py` detects that no valid item names were entered and shows
`st.warning("Please enter at least one food item before analyzing.")` instead of calling the AI
engine or crashing. (The engine itself was also tested directly with an empty list and returns a
safe empty-but-valid result rather than erroring, as a second layer of protection.)

---

## Case 4 — Larger, mixed hostel-mess-style inventory (for your own testing)

Suggested input to try yourself (not run in this build, since it's meant for you to test live
with your API key and see fresh output):

| Item | Quantity | Freshness / Age | Expiry info |
|---|---|---|---|
| Cooked rice | 2 kg | cooked this morning | |
| Mixed vegetable curry | | made yesterday evening | |
| Spinach | 1 bunch | bought 3 days ago | |
| Potatoes | 5 | | |
| Curd | 1 bowl | | best before today |
| Bananas | 6 | a couple look very ripe | |

**People:** 40 (simulating a small hostel mess)

**What to check:** that the model reasonably separates the very perishable/cooked items (curry,
spinach, curd) from the durable ones (potatoes), gives sensible reuse ideas at that quantity, and
does not invent a specific expiry date for anything you didn't give a date for.
