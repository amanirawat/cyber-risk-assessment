"""Build a prioritized remediation plan from an assessment.

Each control gap becomes one action item:

  risk reduction = current risk - risk if the control were fully in place
                   (likelihood drops to 1, impact stays the same)
  priority score = risk reduction / effort   (effort: low 1, medium 2, high 3)

Items are grouped into three phases leadership can act on:

  Now   (0-30 days)   High/Critical risks that are low effort: quick wins
  Next  (30-90 days)  remaining High/Critical risks, plus other low-effort fixes
  Later (90+ days)    everything else

The plan also projects the risk index after each phase, so leadership can see
what each phase actually buys them.
"""

from __future__ import annotations

from dataclasses import dataclass

from .questionnaire import Questionnaire
from .scoring import LIKELIHOOD, Assessment, risk_index_for

EFFORT_WEIGHT = {"low": 1, "medium": 2, "high": 3}
PHASES = ["Now (0-30 days)", "Next (30-90 days)", "Later (90+ days)"]


@dataclass
class ActionItem:
    rank: int
    finding_id: str
    control: str
    area_name: str
    csf: str
    action: str
    why: str
    effort: str
    cost: str
    current_risk: int
    rating: str
    risk_reduction: int
    priority: float
    phase: str


@dataclass
class Plan:
    items: list[ActionItem]
    risk_index_now: float
    risk_index_after: dict[str, float]   # phase -> projected risk index once complete

    def by_phase(self) -> dict[str, list[ActionItem]]:
        return {p: [i for i in self.items if i.phase == p] for p in PHASES}


def _phase(rating: str, effort: str) -> str:
    severe = rating in ("Critical", "High")
    if severe and effort == "low":
        return PHASES[0]
    if severe or effort == "low":
        return PHASES[1]
    return PHASES[2]


def build_plan(qn: Questionnaire, assessment: Assessment) -> Plan:
    questions = qn.by_id()
    drafts = []
    for f in assessment.gaps:
        rem = questions[f.id].remediation
        target_risk = LIKELIHOOD[3] * f.impact
        reduction = f.risk - target_risk
        priority = round(reduction / EFFORT_WEIGHT[rem["effort"]], 2)
        drafts.append(dict(
            finding_id=f.id, control=f.control, area_name=f.area_name, csf=f.csf,
            action=rem["action"], why=rem["why"], effort=rem["effort"], cost=rem["cost"],
            current_risk=f.risk, rating=f.rating, risk_reduction=reduction,
            priority=priority, phase=_phase(f.rating, rem["effort"]),
        ))

    drafts.sort(key=lambda d: (PHASES.index(d["phase"]), -d["priority"], -d["current_risk"], d["finding_id"]))
    items = [ActionItem(rank=i, **d) for i, d in enumerate(drafts, start=1)]

    # Project the risk index as each phase is completed.
    remaining = sum(f.risk for f in assessment.findings)
    after = {}
    for phase in PHASES:
        remaining -= sum(i.risk_reduction for i in items if i.phase == phase)
        after[phase] = risk_index_for(remaining, assessment.findings)

    return Plan(items, assessment.risk_index, after)
