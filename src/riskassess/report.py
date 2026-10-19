"""Render an assessment as Markdown (renders on GitHub) or a self-contained HTML report."""

from __future__ import annotations

import html
import json
from dataclasses import asdict
from datetime import date

from .remediation import PHASES, Plan
from .scoring import Assessment

RATING_COLORS = {"Critical": "#b42318", "High": "#dc6803", "Medium": "#ca8504", "Low": "#079455"}
COST_LABEL = {"$": "Low cost", "$$": "Moderate cost", "$$$": "Significant cost"}


def to_json(assessment: Assessment, plan: Plan, summary: str) -> str:
    return json.dumps({
        "company": assessment.company,
        "summary": summary,
        "overall_maturity_pct": assessment.overall_maturity,
        "risk_index": assessment.risk_index,
        "rating_counts": assessment.rating_counts,
        "areas": [asdict(a) for a in assessment.areas],
        "findings": [asdict(f) for f in assessment.findings],
        "plan": [asdict(i) for i in plan.items],
        "risk_index_after": plan.risk_index_after,
    }, indent=2)


# --------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------

def _bar(pct: float, width: int = 20) -> str:
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def to_markdown(assessment: Assessment, plan: Plan, summary: str) -> str:
    c = assessment.company
    out = [
        f"# Cyber Risk Assessment: {c.get('name', 'Company')}",
        "",
        f"*{c.get('industry', '')} · {c.get('employees', '?')} employees · "
        f"{'Handles sensitive data' if c.get('handles_sensitive_data') else 'No sensitive data flagged'} · "
        f"Generated {date.today().isoformat()}*",
        "",
        "> Fictional organization, created to demonstrate the assessment tool.",
        "",
        "## Executive summary",
        "",
        summary,
        "",
        "| Overall maturity | Risk index | Critical | High | Medium | Low |",
        "|---|---|---|---|---|---|",
        f"| {assessment.overall_maturity:g}% | {assessment.risk_index:g} / 100 | "
        + " | ".join(str(assessment.rating_counts[r]) for r in ("Critical", "High", "Medium", "Low")) + " |",
        "",
        "## Maturity by control area",
        "",
        "| Area | NIST CSF 2.0 | Maturity | | Gaps | Worst rating |",
        "|---|---|---|---|---|---|",
    ]
    for a in sorted(assessment.areas, key=lambda a: a.maturity_pct):
        out.append(f"| {a.name} | {a.csf} | {a.maturity_pct:g}% | `{_bar(a.maturity_pct)}` | {a.gaps} | {a.worst_rating} |")

    out += ["", "## Top risks", "", "| # | Control | Area | Current state | Likelihood | Impact | Risk | Rating |",
            "|---|---|---|---|---|---|---|---|"]
    for i, f in enumerate(assessment.top_risks(5), start=1):
        out.append(f"| {i} | {f.control} | {f.area_name} | {f.answer} | {f.likelihood} | {f.impact} | {f.risk} | **{f.rating}** |")

    out += ["", "## Remediation plan", ""]
    prev = plan.risk_index_now
    for phase, items in plan.by_phase().items():
        if not items:
            continue
        after = plan.risk_index_after[phase]
        out += [f"### {phase}: risk index {prev:g} → {after:g}", "",
                "| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |", "|---|---|---|---|---|---|---|"]
        for it in items:
            out.append(f"| {it.rank} | {it.control} | {it.action} | {it.why} | {it.effort.title()} | {it.cost} | −{it.risk_reduction} |")
        out.append("")
        prev = after

    out += ["## Method", "",
            "Each control is scored 0-3 for maturity. Likelihood (1-5) comes from maturity; impact (1-5) is set per "
            "control and raised by 1 for data-related controls when sensitive data is held. "
            "Risk = likelihood × impact (1-25): Low 1-5, Medium 6-11, High 12-19, Critical 20-25. "
            "The risk index scales total risk from 0 (every control strong) to 100 (every control missing). "
            "Remediation items are ranked by risk reduction divided by effort.", ""]
    return "\n".join(out)


# --------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------

def _heat_color(lik: int, imp: int) -> str:
    score = lik * imp
    if score >= 20:
        return "#fda29b"
    if score >= 12:
        return "#fec84b"
    if score >= 6:
        return "#fef0c7"
    return "#d1fadf"


def to_html(assessment: Assessment, plan: Plan, summary: str) -> str:
    c = assessment.company
    e = html.escape

    area_rows = "".join(
        f"<div class='bar-row'><div class='bar-label'>{e(a.name)}</div><div class='bar-line'>"
        f"<span class='bar-track'><span class='bar-fill' style='width:{a.maturity_pct}%'></span></span>"
        f"<span class='bar-val'>{a.maturity_pct:g}%</span></div></div>"
        for a in sorted(assessment.areas, key=lambda a: a.maturity_pct)
    )

    heat = "<table class='heat'><tr><th></th>" + "".join(f"<th>{i}</th>" for i in range(1, 6)) + "</tr>"
    for lik in range(5, 0, -1):
        heat += f"<tr><th>{lik}</th>"
        for imp in range(1, 6):
            n = assessment.heatmap[lik - 1][imp - 1]
            heat += f"<td style='background:{_heat_color(lik, imp)}'>{n or ''}</td>"
        heat += "</tr>"
    heat += "</table><p class='axis'>Rows: likelihood (5 = most likely) · Columns: impact (5 = most severe) · Cells: number of controls</p>"

    risks = "".join(
        f"<tr><td><strong>{e(f.control)}</strong><br><span class='why'>{e(f.area_name)}</span></td><td>{e(f.answer)}</td><td>{f.risk}</td>"
        f"<td><span class='pill' style='background:{RATING_COLORS[f.rating]}'>{f.rating}</span></td></tr>"
        for f in assessment.top_risks(5)
    )

    phases_html = ""
    prev = plan.risk_index_now
    for phase, items in plan.by_phase().items():
        if not items:
            continue
        after = plan.risk_index_after[phase]
        rows = "".join(
            f"<tr><td>{it.rank}</td><td><span class='why'>{e(it.control)}</span><br><strong>{e(it.action)}</strong><br><span class='why'>{e(it.why)}</span></td>"
            f"<td>{it.effort.title()}</td><td title='{COST_LABEL[it.cost]}'>{it.cost}</td><td>−{it.risk_reduction}</td></tr>"
            for it in items
        )
        phases_html += (f"<h3>{e(phase)} <span class='delta'>risk index {prev:g} → {after:g}</span></h3>"
                        f"<table><tr><th>#</th><th>Action</th><th>Effort</th><th>Cost</th><th>Risk ↓</th></tr>{rows}</table>")
        prev = after

    counts = "".join(
        f"<div class='stat'><div class='num' style='color:{RATING_COLORS[r]}'>{assessment.rating_counts[r]}</div><div>{r}</div></div>"
        for r in ("Critical", "High", "Medium", "Low")
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cyber Risk Assessment - {e(c.get('name', 'Company'))}</title>
<style>
:root {{ --ink:#101828; --muted:#475467; --line:#eaecf0; --accent:#1f3a5f; --bg:#ffffff; }}
* {{ box-sizing:border-box; }}
body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; color:var(--ink); background:var(--bg);
       max-width: 960px; margin: 0 auto; padding: 32px 16px 64px; line-height:1.5; }}
h1 {{ color:var(--accent); margin:0 0 4px; font-size:28px; }}
h2 {{ color:var(--accent); border-bottom:2px solid var(--line); padding-bottom:6px; margin-top:36px; font-size:20px; }}
h3 {{ font-size:16px; margin:24px 0 8px; }}
.sub {{ color:var(--muted); margin:0; }}
.note {{ font-size:13px; color:var(--muted); background:#f9fafb; border:1px solid var(--line); padding:6px 10px; border-radius:6px; display:inline-block; margin-top:10px; }}
.summary {{ background:#f5f8fc; border-left:4px solid var(--accent); padding:14px 18px; border-radius:4px; }}
.stats {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:16px; }}
.stat {{ flex:1 1 120px; border:1px solid var(--line); border-radius:8px; padding:12px; text-align:center; color:var(--muted); font-size:13px; }}
.stat .num {{ font-size:26px; font-weight:700; color:var(--ink); }}
.bar-row {{ margin:10px 0; }}
.bar-label {{ font-size:14px; margin-bottom:3px; }}
.bar-line {{ display:flex; align-items:center; gap:10px; }}
.bar-track {{ flex:1; display:block; height:14px; background:#f2f4f7; border-radius:7px; overflow:hidden; }}
.bar-fill {{ display:block; height:100%; background:var(--accent); }}
.bar-val {{ flex:0 0 52px; text-align:right; font-variant-numeric:tabular-nums; font-size:14px; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th, td {{ border-bottom:1px solid var(--line); padding:8px; text-align:left; vertical-align:top; }}
th {{ color:var(--muted); font-weight:600; }}
.heat {{ width:auto; }} .heat td, .heat th {{ width:48px; height:40px; text-align:center; border:1px solid #fff; }}
.axis {{ font-size:12px; color:var(--muted); }}
.pill {{ color:#fff; border-radius:10px; padding:2px 8px; font-size:12px; font-weight:600; }}
.why {{ color:var(--muted); font-size:13px; }}
.delta {{ font-weight:400; color:var(--muted); font-size:13px; margin-left:8px; }}
.grid {{ display:grid; grid-template-columns: 1fr 1fr; gap:24px; }}
@media (max-width: 720px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style></head><body>
<h1>Cyber Risk Assessment</h1>
<p class="sub"><strong>{e(c.get('name', 'Company'))}</strong> · {e(c.get('industry', ''))} · {c.get('employees', '?')} employees · {date.today().isoformat()}</p>
<span class="note">Fictional organization, created to demonstrate the assessment tool</span>

<h2>Executive summary</h2>
<div class="summary">{e(summary)}</div>
<div class="stats">
  <div class="stat"><div class="num">{assessment.overall_maturity:g}%</div><div>Overall maturity</div></div>
  <div class="stat"><div class="num">{assessment.risk_index:g}</div><div>Risk index (0-100)</div></div>
  {counts}
</div>

<div class="grid">
  <div><h2>Maturity by area</h2>{area_rows}</div>
  <div><h2>Risk heatmap</h2>{heat}</div>
</div>

<h2>Top risks</h2>
<table><tr><th>Control</th><th>Current state</th><th>Risk</th><th>Rating</th></tr>{risks}</table>

<h2>Remediation plan</h2>
{phases_html}

<h2>Method</h2>
<p class="why">Each control is scored 0-3 for maturity and mapped to NIST CSF 2.0. Likelihood (1-5) comes from maturity; impact (1-5) is set per control and raised by 1 for data-related controls when sensitive data is held. Risk = likelihood × impact (Low 1-5, Medium 6-11, High 12-19, Critical 20-25). The risk index scales total risk from 0 (every control strong) to 100 (every control missing). Actions are ranked by risk reduction ÷ effort.</p>
</body></html>"""
