"""Streamlit web UI.  Run with:  streamlit run app.py"""

import re
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from riskassess.questionnaire import list_profiles, load_profile, load_questionnaire  # noqa: E402
from riskassess.remediation import PHASES, build_plan  # noqa: E402
from riskassess.report import RATING_COLORS, to_html, to_markdown  # noqa: E402
from riskassess.scoring import assess  # noqa: E402
from riskassess.summary import executive_summary  # noqa: E402

st.set_page_config(page_title="Cyber Risk Assessment", page_icon="🛡️", layout="wide")
qn = load_questionnaire()

st.title("🛡️ AI Cyber Risk Assessment Assistant")
st.caption("Answer 18 questions mapped to NIST CSF 2.0 and get a scored risk profile plus a prioritized "
           "remediation plan written for non-technical leadership.")

# ---------------- Sidebar: company + starting point ----------------
with st.sidebar:
    st.header("Company")
    choice = st.selectbox("Start from", ["Blank questionnaire"] + list_profiles())
    base = load_profile(choice) if choice != "Blank questionnaire" else {
        "company": {"name": "My Company", "industry": "", "employees": 10, "handles_sensitive_data": False},
        "answers": {q.id: 1 for q in qn.questions},
    }
    if st.session_state.get("loaded") != choice:
        st.session_state["loaded"] = choice
        for q in qn.questions:
            st.session_state[q.id] = base["answers"][q.id]
    company = dict(base["company"])
    company["name"] = st.text_input("Name", company["name"])
    company["industry"] = st.text_input("Industry", company.get("industry", ""))
    company["employees"] = st.number_input("Employees", min_value=1, value=int(company.get("employees") or 1))
    company["handles_sensitive_data"] = st.checkbox(
        "Stores sensitive data (customer, health, payment)", value=company.get("handles_sensitive_data", False))
    if choice != "Blank questionnaire":
        st.info("Sample profiles are fictional companies.")

# ---------------- Questionnaire ----------------
left, right = st.columns([1, 1.25])
with left:
    st.subheader("Questionnaire")
    for area in qn.areas:
        with st.expander(f"{area['name']}  ·  {area['csf']}"):
            for q in [q for q in qn.questions if q.area == area["id"]]:
                opts = sorted(q.options, key=lambda o: -o["maturity"])
                st.radio(q.text, [o["maturity"] for o in opts], key=q.id,
                         format_func=lambda m, q=q: q.label_for(m))

answers = {q.id: st.session_state[q.id] for q in qn.questions}
assessment = assess(qn, {"company": company, "answers": answers})
plan = build_plan(qn, assessment)
summary, mode_used = executive_summary(assessment, plan)

# ---------------- Results ----------------
with right:
    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall maturity", f"{assessment.overall_maturity:g}%")
    c2.metric("Risk index", f"{assessment.risk_index:g}")
    c3.metric("Critical", assessment.rating_counts["Critical"])
    c4.metric("High", assessment.rating_counts["High"])

    st.markdown("**Executive summary**")
    st.info(summary)
    st.caption(f"Summary mode: {mode_used}")

    st.markdown("**Maturity by area (%)**")
    st.bar_chart({a.name: a.maturity_pct for a in assessment.areas}, horizontal=True)

    st.markdown("**Top risks**")
    for f in assessment.top_risks(5):
        st.markdown(
            f"<span style='background:{RATING_COLORS[f.rating]};color:white;padding:2px 8px;"
            f"border-radius:10px;font-size:12px'>{f.rating} · {f.risk}</span> "
            f"**{f.control}** ({f.area_name}): {f.answer}", unsafe_allow_html=True)

st.divider()
st.subheader("Prioritized remediation plan")
prev = plan.risk_index_now
cols = st.columns(3)
for col, (phase, items) in zip(cols, plan.by_phase().items()):
    after = plan.risk_index_after[phase]
    with col:
        st.markdown(f"#### {phase}")
        st.caption(f"Risk index {prev:g} → {after:g}")
        if not items:
            st.write("Nothing in this phase.")
        for it in items:
            st.markdown(f"**{it.rank}. {it.control}:** {it.action}  \n{it.why}  \n"
                        f"*Effort: {it.effort} · Cost: {it.cost} · Risk ↓ {it.risk_reduction}*")
    prev = after

slug = re.sub(r"[^a-z0-9]+", "-", company["name"].lower()).strip("-")
d1, d2 = st.columns(2)
d1.download_button("Download HTML report", to_html(assessment, plan, summary), f"{slug}.html", "text/html")
d2.download_button("Download Markdown report", to_markdown(assessment, plan, summary), f"{slug}.md", "text/markdown")
