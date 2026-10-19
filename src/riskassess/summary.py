"""Executive summary for non-technical leadership.

Two modes:
  * template (default, free, offline): a fixed, plain-language summary built
    directly from the scored results.
  * llm (optional): if ANTHROPIC_API_KEY is set, Claude rewrites the summary in
    a more natural voice, using ONLY the structured facts it is given.

Guardrail: every number in an LLM-written summary must appear in the facts.
If the model introduces a number that isn't in the assessment, the summary is
rejected and the template version is used instead, so leadership never sees an
invented statistic.
"""

from __future__ import annotations

import json
import os
import re

from .remediation import PHASES, Plan
from .scoring import Assessment

DEFAULT_MODEL = os.environ.get("RISKASSESS_MODEL", "claude-haiku-5-5")
_NUMBER = re.compile(r"\d+(?:\.\d+)?")


def posture_label(risk_index: float) -> str:
    if risk_index >= 60:
        return "high risk"
    if risk_index >= 40:
        return "elevated risk"
    if risk_index >= 25:
        return "moderate risk"
    return "low risk"


def facts(assessment: Assessment, plan: Plan) -> dict:
    by_phase = plan.by_phase()
    weakest = sorted(assessment.areas, key=lambda a: a.maturity_pct)[:2]
    return {
        "company": assessment.company.get("name", "The company"),
        "overall_maturity_pct": assessment.overall_maturity,
        "risk_index": assessment.risk_index,
        "posture": posture_label(assessment.risk_index),
        "controls_assessed": len(assessment.findings),
        "gaps": len(assessment.gaps),
        "critical": assessment.rating_counts["Critical"],
        "high": assessment.rating_counts["High"],
        "weakest_areas": [{"name": a.name, "maturity_pct": a.maturity_pct} for a in weakest],
        "top_risks": [{"control": f.control, "area": f.area_name, "current_state": f.answer, "rating": f.rating}
                      for f in assessment.top_risks(3)],
        "quick_wins": len(by_phase[PHASES[0]]),
        "risk_index_after_now": plan.risk_index_after[PHASES[0]],
        "risk_index_after_all": plan.risk_index_after[PHASES[2]],
    }


def _severity_clause(f: dict) -> str:
    parts = []
    if f["critical"]:
        parts.append(f"{f['critical']} rated Critical")
    if f["high"]:
        parts.append(f"{f['high']} rated High")
    if not parts:
        return "none of them rated High or Critical"
    return "including " + " and ".join(parts)


def template_summary(f: dict) -> str:
    weakest = " and ".join(f"{a['name']} ({a['maturity_pct']:g}%)" for a in f["weakest_areas"])
    drop = round(f["risk_index"] - f["risk_index_after_now"], 1)
    if f["gaps"] == f["controls_assessed"]:
        gaps = f"All {f['controls_assessed']} controls reviewed have gaps"
    elif f["gaps"] == 0:
        gaps = f"All {f['controls_assessed']} controls reviewed are fully in place"
    else:
        gaps = f"{f['gaps']} of {f['controls_assessed']} controls reviewed have gaps"
    lines = [
        f"{f['company']} is at {f['posture']}. Overall security maturity is {f['overall_maturity_pct']:g}% "
        f"and the risk index is {f['risk_index']:g} out of 100.",
        f"{gaps}, {_severity_clause(f)}." if f["gaps"] else f"{gaps}.",
        f"The weakest areas are {weakest}.",
    ]
    if f["quick_wins"]:
        lines.append(
            f"There are {f['quick_wins']} quick wins that can be completed in the next 30 days at low cost. "
            f"Doing them lowers the risk index from {f['risk_index']:g} to {f['risk_index_after_now']:g}, "
            f"a reduction of {drop:g} points."
        )
    elif f["critical"] or f["high"]:
        lines.append("None of the most serious risks has a low-effort fix, so start with the 30-90 day items.")
    elif f["gaps"]:
        lines.append("The remaining gaps are improvements to schedule over the next quarter rather than urgent fixes.")
    if f["gaps"]:
        lines.append(f"Completing the full plan brings the risk index down to {f['risk_index_after_all']:g}.")
    return " ".join(lines)


SYSTEM_PROMPT = """You write executive summaries of cybersecurity risk assessments for
non-technical small-business owners. Use ONLY the facts in the JSON provided.
Rules:
- 4 to 6 sentences, plain language, no jargon, no bullet points.
- Do not introduce any number that is not in the facts.
- Lead with overall posture, then the biggest risks, then what to do first and what it buys them."""


def allowed_numbers(f: dict) -> set[str]:
    text = json.dumps(f)
    nums = set(_NUMBER.findall(text))
    drop = round(f["risk_index"] - f["risk_index_after_now"], 1)
    nums |= {f"{drop:g}", "30", "90", "100", "0"}
    # Accept "34" for "34.0" and similar formatting differences.
    nums |= {n.rstrip("0").rstrip(".") for n in nums if "." in n}
    return nums


def check_numbers(text: str, f: dict) -> list[str]:
    allowed = allowed_numbers(f)
    return [n for n in _NUMBER.findall(text) if n not in allowed and n.rstrip("0").rstrip(".") not in allowed]


def llm_summary(f: dict, model: str = DEFAULT_MODEL) -> str:
    import anthropic  # optional dependency

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": json.dumps(f, indent=2)}],
    )
    return "".join(b.text for b in response.content if b.type == "text").strip()


def executive_summary(assessment: Assessment, plan: Plan, mode: str | None = None) -> tuple[str, str]:
    """Return (summary_text, mode_used)."""
    f = facts(assessment, plan)
    if mode is None:
        mode = "llm" if os.environ.get("ANTHROPIC_API_KEY") else "template"
    if mode == "llm":
        try:
            text = llm_summary(f)
            if not check_numbers(text, f):
                return text, "llm"
            return template_summary(f), "template (LLM summary rejected: unverified numbers)"
        except Exception as exc:  # network, auth, missing package
            return template_summary(f), f"template (LLM unavailable: {type(exc).__name__})"
    return template_summary(f), "template"
