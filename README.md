# AI Cyber Risk Assessment Assistant

A guided security assessment for small businesses. It walks an organization through **18 questions across 6 control areas** mapped to the **NIST Cybersecurity Framework 2.0**, converts the answers into a **scored risk profile**, and generates a **prioritized remediation plan written for non-technical leadership**.

```
$ riskassess assess larkspur-family-dental

Larkspur Family Dental
  Overall maturity   19.8%
  Risk index         85.1 / 100
  Ratings            Low 0, Medium 0, High 8, Critical 10
  Plan               18 actions; risk index after quick wins 39.9, after full plan 0
  Report             reports/larkspur-family-dental.html
```

**Sample reports** for three fictional companies: [Larkspur Family Dental](reports/larkspur-family-dental.md) (weak posture) · [Bramblewood Logistics](reports/bramblewood-logistics.md) (mixed) · [Cedar & Finch Accounting](reports/cedar-finch-accounting.md) (strong)

## Why this exists

Small businesses rarely have a security team, and technical audit findings don't help an owner decide what to do on Monday. This tool turns a short questionnaire into the three things leadership actually needs: **how exposed they are, which gaps matter most, and what to fix first for the least money and effort.**

## How it works

```
questionnaire (18 controls, 6 areas, NIST CSF 2.0)
        │  1. Answer: each control is rated 0-3 for maturity
        ▼
  2. Score each control
     likelihood 1-5  ← from maturity (weaker control = more likely compromise)
     impact     1-5  ← set per control; +1 for data controls if the business
                       holds sensitive data (patient, financial, payment)
     risk = likelihood × impact  →  Low 1-5 · Medium 6-11 · High 12-19 · Critical 20-25
        │
        ▼
  3. Roll up: maturity % per area · impact-weighted overall maturity ·
     risk index 0-100 (0 = every control strong, 100 = every control missing) ·
     likelihood × impact heatmap
        │
        ▼
  4. Plan: every gap becomes an action ranked by risk reduction ÷ effort,
     grouped into Now (0-30 days) / Next (30-90) / Later (90+), with the
     projected risk index after each phase
        │
        ▼
  5. Executive summary in plain language, then a Markdown, HTML or JSON report
```

| Control area | NIST CSF 2.0 | Controls |
|---|---|---|
| Access Control | PR.AA | MFA, admin rights, offboarding, password management |
| Backups & Recovery | PR.DS / RC.RP | Backup frequency, offline/immutable copies, restore testing |
| Patching & Vulnerability Management | PR.PS / ID.RA / ID.AM / DE.CM | Updates, end-of-life software, asset inventory, endpoint protection |
| Security Awareness Training | PR.AT | Training cadence, phishing simulations, reporting channel |
| Incident Response | RS.MA | Written IR plan, emergency contacts |
| Data Protection | PR.DS | Device encryption, sensitive-data access |

| Component | File |
|---|---|
| Questionnaire, controls & remediation library | `data/questionnaire.json` |
| Fictional company profiles | `data/profiles/` |
| Risk scoring | `src/riskassess/scoring.py` |
| Remediation planner | `src/riskassess/remediation.py` |
| Executive summary (template + optional LLM) | `src/riskassess/summary.py` |
| Reports (Markdown / HTML / JSON) | `src/riskassess/report.py` |
| Scoring-model validation | `src/riskassess/validate.py` |
| Web UI | `app.py` (Streamlit) |

### Where the AI comes in, and how it is kept honest

By default the executive summary is generated from a template, so the tool is free and runs offline. With an `ANTHROPIC_API_KEY` set, Claude rewrites the summary in a more natural voice using **only the structured results**. Every number in the AI-written summary is then checked against the assessment, and **if the model introduces any number that isn't in the results, its summary is rejected** and the template version is used. Leadership never sees an invented statistic.

## Results

### Scoring-model validation (`riskassess validate`)

A risk score is only useful if it behaves sensibly, so the model is tested against **1,000 simulated companies** with random answers:

| Check | What it verifies | Result |
|---|---|---|
| Monotonicity | Improving any single control never raises the risk index, and always lowers that control's own risk | **13,435 / 13,435** (100%) |
| Bounds | Every risk is 1-25; every index and percentage is 0-100 | **1,000 / 1,000** (100%) |
| Plan coverage | Every control gap gets exactly one remediation action | **1,000 / 1,000** (100%) |
| Plan payoff | The projected risk index falls with each phase and reaches 0 when the plan is complete | **1,000 / 1,000** (100%) |
| Profile ordering | Weak > mixed > strong sample companies | **Pass** (85.1 > 36.8 > 6.8) |

Across the simulations, the areas that move the risk index most are **Access Control** (r = 0.49), **Backups & Recovery** (0.45) and **Patching** (0.44). These three areas carry the highest impact weights, so they're where improvements pay off most.

### Sample companies (fictional)

| Company | Profile | Overall maturity | Risk index | Critical / High | Risk index after 30-day quick wins |
|---|---|---|---|---|---|
| Larkspur Family Dental | 14 staff, patient data, informal IT | 19.8% | 85.1 | 10 / 8 | **39.9** (−45.2 from 10 low-cost actions) |
| Bramblewood Logistics | 48 staff, outsourced IT | 60% | 36.8 | 0 / 5 | **29.3** (−7.5 from 2 actions) |
| Cedar & Finch Accounting | 22 staff, managed security provider | 91% | 6.8 | 0 / 0 | No urgent items |

## Quick start

Requires Python 3.10+. The core tool has **no dependencies** beyond the standard library.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[ui,dev]"

riskassess list                                  # sample companies
riskassess assess larkspur-family-dental          # HTML report in reports/
riskassess assess bramblewood-logistics --format md
riskassess interview                             # answer the questionnaire yourself
riskassess validate                              # run the validation suite
pytest                                           # 20 tests

streamlit run app.py                             # web UI at http://localhost:8501
```

### Optional: AI-written executive summary

```bash
pip install -e ".[llm]"
export ANTHROPIC_API_KEY=your-key
riskassess assess larkspur-family-dental --summary llm
```

## Limitations

- Likelihood and impact values are **expert-judgment weights** for a typical small business, not actuarial probabilities. They're defined in `data/questionnaire.json` so they can be adjusted for a specific organization.
- The questionnaire is self-reported. It measures what people say is in place, not what a technical scan would find.
- All sample companies are fictional.
- This is a portfolio project, not a substitute for a professional security assessment.

## Roadmap

- [ ] Weight controls by industry (healthcare, finance, retail)
- [ ] Export the remediation plan to a task tracker (CSV / Jira)
- [ ] Track progress over time by comparing two assessments of the same company
- [ ] Add CIS Controls v8 mappings alongside NIST CSF 2.0

## License

MIT
