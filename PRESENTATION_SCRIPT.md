# Presentation Script (~1–2 minutes)

Structure: Problem → Users → AI Solution → How it works → SDG → Impact.
Feel free to adjust the wording to sound like you — this is a starting draft, timed at roughly
100-130 seconds when read at a natural pace.

---

**Problem**
"A lot of food gets wasted not because people don't care, but because it's genuinely hard to
keep track of what's in the fridge, what's about to go bad, and what to do with leftovers. That
happens in homes, hostels, and college messes every single day.

**Users**
This is for anyone managing their own food — students in hostels, households, or even a college
mess — who wants a simple way to reduce what they're throwing away.

**AI Solution**
So I built an AI Food Waste Reduction Assistant. You type in what food you currently have — for
example, some tomatoes, half a loaf of bread, leftover dal from yesterday, and a kilo of rice —
and the assistant tells you what to use first, what can wait, how to reuse your leftovers, and
one simple tip to avoid over-buying next time.

**How it works**
Under the hood, it uses a large language model, guided by a small curated knowledge base of
general food-storage guidance — that's a lightweight retrieval step before the AI generates its
answer. I deliberately constrained the AI so it never invents an exact expiry date and never
states uncertain food-safety claims as fact — if it's unsure, it says so and tells you to check
official guidance instead.

**SDG**
This directly targets SDG 12, Responsible Consumption and Production, by helping people make
small, better decisions about the food they already have, instead of letting it go to waste.

**Impact**
The expected impact is fairly modest but real: less food thrown away means less wasted money,
and less organic waste sitting in landfills producing methane. I want to be upfront that this is
a prototype — I haven't run a formal study, so I'm not claiming a measured percentage reduction,
just a reasonable, well-scoped expected impact."

---

**Optional closing line if asked a question live:**
"The main limitation right now is that the assistant only knows what you tell it — it can't see
or smell your food — so it's a decision-support tool, not a food-safety authority."
