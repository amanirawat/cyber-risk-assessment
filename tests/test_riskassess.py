import pytest

from riskassess.questionnaire import load_profile, load_questionnaire
from riskassess.remediation import PHASES, build_plan
from riskassess.report import to_html, to_markdown
from riskassess.scoring import assess, rating_for
from riskassess.summary import check_numbers, executive_summary, facts
from riskassess.validate import run_validation


@pytest.fixture(scope="module")
def qn():
    return load_questionnaire()


def all_at(qn, level, sensitive=False):
    return {"company": {"name": "T", "handles_sensitive_data": sensitive},
            "answers": {q.id: level for q in qn.questions}}


def test_questionnaire_shape(qn):
    assert len(qn.questions) == 18
    assert len(qn.areas) == 6


@pytest.mark.parametrize("score,rating", [(1, "Low"), (5, "Low"), (6, "Medium"), (11, "Medium"),
                                          (12, "High"), (19, "High"), (20, "Critical"), (25, "Critical")])
def test_rating_thresholds(score, rating):
    assert rating_for(score) == rating


def test_perfect_and_worst_scores(qn):
    best, worst = assess(qn, all_at(qn, 3)), assess(qn, all_at(qn, 0))
    assert best.overall_maturity == 100 and best.risk_index == 0.0
    assert worst.overall_maturity == 0 and worst.risk_index == 100.0
    assert not best.gaps and len(worst.gaps) == 18


def test_sensitive_data_raises_impact(qn):
    plain = assess(qn, all_at(qn, 1, sensitive=False))
    sens = assess(qn, all_at(qn, 1, sensitive=True))
    dp1_plain = next(f for f in plain.findings if f.id == "DP1")
    dp1_sens = next(f for f in sens.findings if f.id == "DP1")
    assert dp1_sens.impact == dp1_plain.impact + 1
    ac1 = next(f for f in sens.findings if f.id == "AC1")
    assert ac1.impact == 5      # not bumped, already capped


def test_missing_answers_rejected(qn):
    profile = all_at(qn, 2)
    del profile["answers"]["BK1"]
    with pytest.raises(ValueError, match="BK1"):
        assess(qn, profile)


def test_plan_covers_every_gap_and_projects_downward(qn):
    a = assess(qn, load_profile("larkspur-family-dental"))
    plan = build_plan(qn, a)
    assert sorted(i.finding_id for i in plan.items) == sorted(f.id for f in a.gaps)
    seq = [plan.risk_index_now] + [plan.risk_index_after[p] for p in PHASES]
    assert seq == sorted(seq, reverse=True)


def test_quick_wins_are_severe_and_low_effort(qn):
    plan = build_plan(qn, assess(qn, load_profile("larkspur-family-dental")))
    for it in plan.by_phase()[PHASES[0]]:
        assert it.effort == "low" and it.rating in ("Critical", "High")


def test_sample_profiles_rank_in_expected_order(qn):
    r = {p: assess(qn, load_profile(p)).risk_index
         for p in ("larkspur-family-dental", "bramblewood-logistics", "cedar-finch-accounting")}
    assert r["larkspur-family-dental"] > r["bramblewood-logistics"] > r["cedar-finch-accounting"]


def test_template_summary_uses_only_real_numbers(qn):
    a = assess(qn, load_profile("bramblewood-logistics"))
    plan = build_plan(qn, a)
    text, mode = executive_summary(a, plan, mode="template")
    assert mode == "template"
    assert check_numbers(text, facts(a, plan)) == []


def test_number_guard_catches_invented_statistics(qn):
    a = assess(qn, load_profile("bramblewood-logistics"))
    f = facts(a, plan=build_plan(qn, a))
    assert check_numbers("Your risk dropped 73% and you saved $40000.", f) != []


def test_llm_summary_with_invented_number_falls_back(qn, monkeypatch):
    import riskassess.summary as summary_mod

    monkeypatch.setattr(summary_mod, "llm_summary", lambda f: "Risk is 999 out of 100.")
    a = assess(qn, load_profile("bramblewood-logistics"))
    text, mode = executive_summary(a, build_plan(qn, a), mode="llm")
    assert "999" not in text and mode.startswith("template (LLM summary rejected")


def test_reports_render(qn):
    a = assess(qn, load_profile("cedar-finch-accounting"))
    plan = build_plan(qn, a)
    s, _ = executive_summary(a, plan, mode="template")
    assert "Cedar &amp; Finch Accounting" in to_html(a, plan, s)
    assert "## Remediation plan" in to_markdown(a, plan, s)


def test_validation_suite_passes(qn):
    r = run_validation(qn, n=200, seed=7)
    assert all(c["pct"] == 100.0 for c in r["checks"].values())
    assert r["profile_ordering"]["passed"]
