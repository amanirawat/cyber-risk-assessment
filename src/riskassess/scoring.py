"""Turn questionnaire answers into a quantified risk profile.

Model (a standard likelihood x impact risk matrix):

  maturity  0-3   how well the control is in place (3 = strong)
  likelihood 1-5  derived from maturity: a weaker control makes compromise more likely
                  3 -> 1, 2 -> 2, 1 -> 4, 0 -> 5
  impact     1-5  business impact if this control fails; set per question and
                  raised by 1 for data-related controls when the company holds
                  sensitive data (patient, financial, payment records)
  risk      1-25  likelihood x impact

  Rating:  1-5 Low | 6-11 Medium | 12-19 High | 20-25 Critical

Roll-ups:
  area maturity %  average maturity of the area's controls, as a percentage
  overall maturity impact-weighted average maturity across all controls (%)
  risk index 0-100 where total risk sits between the best case (every control
                   strong: 0) and the worst case (every control missing: 100)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .questionnaire import Question, Questionnaire

LIKELIHOOD = {3: 1, 2: 2, 1: 4, 0: 5}
RATINGS = [(5, "Low"), (11, "Medium"), (19, "High"), (25, "Critical")]
RATING_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def rating_for(score: int) -> str:
    for upper, name in RATINGS:
        if score <= upper:
            return name
    raise ValueError(f"risk score {score} out of range")


def risk_index_for(total_risk: float, findings: list) -> float:
    """Scale total risk so all-strong controls = 0 and all-missing controls = 100."""
    floor = sum(LIKELIHOOD[3] * f.impact for f in findings)
    ceiling = sum(LIKELIHOOD[0] * f.impact for f in findings)
    return round(100 * (total_risk - floor) / (ceiling - floor), 1)


def effective_impact(q: Question, handles_sensitive_data: bool) -> int:
    if handles_sensitive_data and q.sensitive_data_bump:
        return min(5, q.impact + 1)
    return q.impact


@dataclass
class Finding:
    id: str
    control: str
    area: str
    area_name: str
    csf: str
    question: str
    answer: str
    maturity: int
    likelihood: int
    impact: int
    risk: int
    rating: str


@dataclass
class AreaScore:
    area: str
    name: str
    csf: str
    maturity_pct: float
    risk_total: int
    risk_max: int
    gaps: int
    worst_rating: str


@dataclass
class Assessment:
    company: dict
    findings: list[Finding]
    areas: list[AreaScore]
    overall_maturity: float
    risk_index: float
    rating_counts: dict[str, int]
    heatmap: list[list[int]] = field(default_factory=list)   # [likelihood-1][impact-1]

    @property
    def gaps(self) -> list[Finding]:
        return [f for f in self.findings if f.maturity < 3]

    def top_risks(self, n: int = 5) -> list[Finding]:
        return sorted(self.gaps, key=lambda f: (-f.risk, f.id))[:n]


def assess(qn: Questionnaire, profile: dict) -> Assessment:
    company = profile.get("company", {})
    answers = profile["answers"]
    sensitive = bool(company.get("handles_sensitive_data"))

    missing = [q.id for q in qn.questions if q.id not in answers]
    if missing:
        raise ValueError(f"profile is missing answers for: {', '.join(missing)}")

    findings = []
    for q in qn.questions:
        m = int(answers[q.id])
        if m not in LIKELIHOOD:
            raise ValueError(f"{q.id}: maturity must be 0-3, got {m}")
        lik, imp = LIKELIHOOD[m], effective_impact(q, sensitive)
        risk = lik * imp
        findings.append(Finding(
            id=q.id, control=q.name, area=q.area, area_name=qn.area_name(q.area), csf=q.csf,
            question=q.text, answer=q.label_for(m), maturity=m,
            likelihood=lik, impact=imp, risk=risk, rating=rating_for(risk),
        ))

    areas = []
    for a in qn.areas:
        fs = [f for f in findings if f.area == a["id"]]
        areas.append(AreaScore(
            area=a["id"], name=a["name"], csf=a["csf"],
            maturity_pct=round(100 * sum(f.maturity for f in fs) / (3 * len(fs)), 1),
            risk_total=sum(f.risk for f in fs),
            risk_max=sum(5 * f.impact for f in fs),
            gaps=sum(f.maturity < 3 for f in fs),
            worst_rating=min((f.rating for f in fs), key=RATING_ORDER.get),
        ))

    weight = sum(f.impact for f in findings)
    overall_maturity = round(100 * sum(f.maturity * f.impact for f in findings) / (3 * weight), 1)
    risk_index = risk_index_for(sum(f.risk for f in findings), findings)

    counts = {name: 0 for _, name in RATINGS}
    for f in findings:
        counts[f.rating] += 1

    heatmap = [[0] * 5 for _ in range(5)]
    for f in findings:
        heatmap[f.likelihood - 1][f.impact - 1] += 1

    return Assessment(company, findings, areas, overall_maturity, risk_index, counts, heatmap)
