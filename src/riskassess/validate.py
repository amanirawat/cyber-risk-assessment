"""Validate the scoring model with simulated assessments.

A risk score is only useful if it behaves sensibly. This runs N random
questionnaires and checks properties the model must always satisfy:

  * Monotonicity: improving any single control never raises the overall risk
    index, and always lowers that control's own risk.
  * Bounds: every risk is 1-25 and every index or percentage is 0-100.
  * Plan coverage: every control gap gets exactly one remediation item.
  * Plan payoff: the projected risk index never goes up as phases complete,
    and completing the full plan reaches the floor (every control at maturity 3).
  * Profile ordering: the weak, mixed and strong sample companies rank in the
    expected order.

It also reports which control areas drive the most variation in the risk index
across the simulations (correlation between area maturity and risk index).
"""

from __future__ import annotations

import random
import statistics

from .questionnaire import Questionnaire, load_profile
from .remediation import PHASES, build_plan
from .scoring import assess


def _random_profile(qn: Questionnaire, rng: random.Random) -> dict:
    return {
        "company": {"name": "Sim", "handles_sensitive_data": rng.random() < 0.5},
        "answers": {q.id: rng.randint(0, 3) for q in qn.questions},
    }


def _pearson(xs: list[float], ys: list[float]) -> float:
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / den if den else 0.0


def run_validation(qn: Questionnaire, n: int = 1000, seed: int = 42) -> dict:
    rng = random.Random(seed)
    checks = {"monotonicity": [0, 0], "bounds": [0, 0], "plan_coverage": [0, 0], "plan_payoff": [0, 0]}
    risk_indices, area_maturity = [], {a["id"]: [] for a in qn.areas}

    for _ in range(n):
        profile = _random_profile(qn, rng)
        a = assess(qn, profile)
        plan = build_plan(qn, a)
        risk_indices.append(a.risk_index)
        for s in a.areas:
            area_maturity[s.area].append(s.maturity_pct)

        # Bounds
        ok = all(1 <= f.risk <= 25 for f in a.findings) and 0 <= a.risk_index <= 100 \
            and 0 <= a.overall_maturity <= 100 and all(0 <= s.maturity_pct <= 100 for s in a.areas)
        checks["bounds"][0] += ok
        checks["bounds"][1] += 1

        # Plan coverage: one item per gap, no extras
        gap_ids = sorted(f.id for f in a.gaps)
        checks["plan_coverage"][0] += sorted(i.finding_id for i in plan.items) == gap_ids
        checks["plan_coverage"][1] += 1

        # Plan payoff: projected index never rises; the full plan reaches the floor
        floor = {"company": profile["company"], "answers": {q.id: 3 for q in qn.questions}}
        seq = [plan.risk_index_now] + [plan.risk_index_after[p] for p in PHASES]
        payoff_ok = all(x >= y for x, y in zip(seq, seq[1:])) and \
            abs(plan.risk_index_after[PHASES[-1]] - assess(qn, floor).risk_index) < 0.11
        checks["plan_payoff"][0] += payoff_ok
        checks["plan_payoff"][1] += 1

        # Monotonicity: improving ANY single control by one step never raises risk
        for q in qn.questions:
            if profile["answers"][q.id] == 3:
                continue
            better = {"company": profile["company"], "answers": dict(profile["answers"])}
            better["answers"][q.id] += 1
            b = assess(qn, better)
            old_f = next(f for f in a.findings if f.id == q.id)
            new_f = next(f for f in b.findings if f.id == q.id)
            checks["monotonicity"][0] += (b.risk_index <= a.risk_index and new_f.risk < old_f.risk)
            checks["monotonicity"][1] += 1

    names = {a["id"]: a["name"] for a in qn.areas}
    drivers = sorted(
        ((names[k], round(abs(_pearson(v, risk_indices)), 3)) for k, v in area_maturity.items()),
        key=lambda t: -t[1],
    )

    samples = {}
    for name in ("larkspur-family-dental", "bramblewood-logistics", "cedar-finch-accounting"):
        try:
            samples[name] = assess(qn, load_profile(name)).risk_index
        except FileNotFoundError:
            pass
    ordering_ok = (len(samples) == 3 and samples["larkspur-family-dental"]
                   > samples["bramblewood-logistics"] > samples["cedar-finch-accounting"])

    return {
        "simulations": n,
        "checks": {k: {"passed": p, "total": t, "pct": round(100 * p / t, 1) if t else 0.0}
                   for k, (p, t) in checks.items()},
        "profile_ordering": {"passed": ordering_ok, "risk_index": samples},
        "risk_index_distribution": {
            "min": min(risk_indices), "median": statistics.median(risk_indices),
            "max": max(risk_indices), "stdev": round(statistics.stdev(risk_indices), 1),
        },
        "area_drivers": drivers,
    }
