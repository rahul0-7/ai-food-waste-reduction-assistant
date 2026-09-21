"""
app.py
------
AI Food Waste Reduction Assistant
1M1B AI for Sustainability Virtual Internship (July-Sept 2026)
Primary SDG: SDG 12 - Responsible Consumption and Production

Run locally:  streamlit run app.py
See README.md for setup and deployment instructions.
"""

# load_dotenv() MUST run before any local module is imported, because
# ai_engine.py reads GEMINI_MODEL at module-level evaluation time.
# Importing ai_engine before load_dotenv() means os.environ.get("GEMINI_MODEL")
# always sees the empty environment and falls back to the hardcoded default.
# On Streamlit Community Cloud (and other cloud hosts) load_dotenv() is a
# no-op — platform-injected env vars are already present before Python starts.
from dotenv import load_dotenv
load_dotenv()

import pandas as pd  # noqa: E402 — must come after load_dotenv()
import streamlit as st  # noqa: E402

from ai_engine import get_ai_recommendations  # noqa: E402

st.set_page_config(
    page_title="AI Food Waste Reduction Assistant",
    page_icon="🥗",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🥗 AI Food Waste Reduction Assistant")
st.caption("An SDG 12 (Responsible Consumption & Production) student project — 1M1B AI for Sustainability Virtual Internship")

st.markdown(
    """
Tell this assistant what food you currently have, and it will suggest **what to use first,
what can wait, how to use up leftovers, and how to avoid over-buying next time** —
so less good food ends up in the bin.
"""
)

with st.expander("📌 The problem this project addresses", expanded=False):
    st.markdown(
        """
Food is unnecessarily wasted in households, hostels, college messes and canteens because people
buy or prepare excessive quantities, forget what food they already have, don't prioritize food
that should be eaten sooner, or don't know how to reuse leftovers. This contributes to avoidable
economic loss and environmental impact (e.g. wasted resources and methane emissions from food
decomposing in landfills), which connects directly to **UN SDG 12: Responsible Consumption and
Production**.

This tool does **not** claim to solve food waste on its own — it is a small, focused decision-support
prototype aimed at one part of the problem: helping an individual or household make slightly
better day-to-day decisions about the food they already have.
"""
    )

with st.expander("🔒 Responsible AI notice — please read", expanded=False):
    st.markdown(
        """
**Fairness** — This tool gives the same type of general guidance to everyone and does not base
suggestions on personal characteristics of the user, only on the food items and details entered.

**Transparency** — Every result below is labelled as either AI-generated or produced by a simple
built-in rule-based fallback (used only if the AI service is unavailable). Suggestions are based on
the information *you* provide plus general, curated food-storage guidance — the assistant does not
know the actual physical condition of your food.

**Ethics** — This is a decision-support tool, not an authority. It is designed to avoid presenting
uncertain food-safety information as settled fact, and it will not invent exact expiry dates that
you did not provide.

**Privacy** — The tool only asks for food item details needed to generate suggestions. It does not
request or store names, contact details, or other personal information, and inputs are not used for
anything beyond generating your results in this session.

**Please use judgement.** If you are ever genuinely unsure whether a food item is still safe to eat,
consult official or local food-safety guidance rather than relying solely on this tool.
"""
    )

st.divider()

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
st.subheader("1. Enter your current food inventory")
st.caption("Quantity, freshness/age and expiry info are optional but improve the quality of suggestions.")

default_rows = pd.DataFrame(
    [
        {"Item": "Tomatoes", "Quantity": "2", "Freshness / Age (optional)": "", "Expiry info (optional)": ""},
        {"Item": "Bread", "Quantity": "half loaf", "Freshness / Age (optional)": "a few days old", "Expiry info (optional)": ""},
        {"Item": "Cooked dal", "Quantity": "", "Freshness / Age (optional)": "cooked yesterday", "Expiry info (optional)": ""},
        {"Item": "Rice", "Quantity": "1 kg", "Freshness / Age (optional)": "uncooked", "Expiry info (optional)": ""},
    ]
)

inventory_df = st.data_editor(
    default_rows,
    num_rows="dynamic",
    use_container_width=True,
    key="inventory_editor",
)

num_people = st.number_input(
    "Approximate number of people eating (optional)",
    min_value=0,
    max_value=50,
    value=0,
    help="Leave at 0 if you'd rather not specify.",
)

analyze_clicked = st.button("🔎 Analyze my food & suggest actions", type="primary")

st.divider()

# ---------------------------------------------------------------------------
# Analysis / results section
# ---------------------------------------------------------------------------
st.subheader("2. Results")

if analyze_clicked:
    items = []
    for _, row in inventory_df.iterrows():
        name = str(row.get("Item", "")).strip()
        if not name or name.lower() == "nan":
            continue
        items.append(
            {
                "name": name,
                "quantity": str(row.get("Quantity", "") or "").strip(),
                "age_or_freshness": str(row.get("Freshness / Age (optional)", "") or "").strip(),
                "expiry": str(row.get("Expiry info (optional)", "") or "").strip(),
            }
        )

    if not items:
        st.warning("Please enter at least one food item before analyzing.")
    else:
        with st.spinner("Analyzing your inventory..."):
            result = get_ai_recommendations(items, num_people if num_people > 0 else None)

        # Transparency banner
        if result.get("mode") == "ai":
            st.success("✅ Suggestions generated by the AI model, grounded with curated food-waste guidance.")
        else:
            st.warning(
                "⚠️ The AI service was unavailable, so these suggestions were produced by a simple "
                "built-in rule-based fallback instead (not the AI model)."
            )
            with st.expander("Technical details"):
                st.code(result.get("fallback_reason", "Unknown reason"))

        st.markdown("#### What you entered")
        st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("##### 🔴 Use First")
            items_uf = result.get("use_first") or []
            if items_uf:
                for x in items_uf:
                    st.markdown(f"- {x}")
            else:
                st.caption("Nothing flagged as urgent based on what you entered.")
        with col2:
            st.markdown("##### 🟠 Use Soon")
            items_us = result.get("use_soon") or []
            if items_us:
                for x in items_us:
                    st.markdown(f"- {x}")
            else:
                st.caption("Nothing flagged here.")
        with col3:
            st.markdown("##### 🟢 Longer Storage")
            items_ls = result.get("longer_storage") or []
            if items_ls:
                for x in items_ls:
                    st.markdown(f"- {x}")
            else:
                st.caption("Nothing flagged here.")

        st.markdown("##### ♻️ Leftover / Reuse Ideas")
        for x in result.get("leftover_ideas") or []:
            st.markdown(f"- {x}")

        st.markdown("##### ✅ Waste-Reduction Actions")
        for x in result.get("waste_reduction_actions") or []:
            st.markdown(f"- {x}")

        st.markdown("##### 🛒 Shopping / Planning Tip")
        st.info(result.get("shopping_planning_tip", ""))

        st.markdown("##### 🌍 Sustainability Impact (expected, not measured)")
        st.info(result.get("sustainability_impact", ""))

        st.markdown("##### ⚠️ Safety Note")
        st.warning(result.get("safety_note", ""))

else:
    st.caption("Fill in your food items above and click **Analyze my food & suggest actions**.")

st.divider()

with st.expander("ℹ️ About this project / SDG 12 alignment"):
    st.markdown(
        """
**Project:** AI Food Waste Reduction Assistant
**Primary SDG:** SDG 12 — Responsible Consumption and Production
**Built for:** 1M1B AI for Sustainability Virtual Internship (July–September 2026)

This prototype uses a large language model (LLM), guided by a small curated knowledge base of
general food-storage and waste-reduction guidance (a lightweight Retrieval-Augmented Generation
approach), to turn a simple list of food items into practical, prioritized suggestions. See
`DOCUMENTATION.md` in the project files for the full write-up, including the design-thinking
process, limitations, and responsible-AI considerations.
"""
    )
