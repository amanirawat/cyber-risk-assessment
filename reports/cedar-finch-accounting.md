# Cyber Risk Assessment: Cedar & Finch Accounting

*Professional services (accounting) · 22 employees · Handles sensitive data · Generated 2026-10-19*

> Fictional organization, created to demonstrate the assessment tool.

## Executive summary

Cedar & Finch Accounting is at low risk. Overall security maturity is 91% and the risk index is 6.8 out of 100. 5 of 18 controls reviewed have gaps, none of them rated High or Critical. The weakest areas are Incident Response (83.3%) and Data Protection (83.3%). The remaining gaps are improvements to schedule over the next quarter rather than urgent fixes. Completing the full plan brings the risk index down to 0.

| Overall maturity | Risk index | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| 91% | 6.8 / 100 | 0 | 0 | 5 | 13 |

## Maturity by control area

| Area | NIST CSF 2.0 | Maturity | | Gaps | Worst rating |
|---|---|---|---|---|---|
| Incident Response | RS.MA | 83.3% | `█████████████████░░░` | 1 | Medium |
| Data Protection | PR.DS | 83.3% | `█████████████████░░░` | 1 | Medium |
| Backups & Recovery | PR.DS / RC.RP | 88.9% | `██████████████████░░` | 1 | Medium |
| Security Awareness Training | PR.AT | 88.9% | `██████████████████░░` | 1 | Medium |
| Patching & Vulnerability Management | PR.PS / ID.RA | 91.7% | `██████████████████░░` | 1 | Medium |
| Access Control | PR.AA | 100% | `████████████████████` | 0 | Low |

## Top risks

| # | Control | Area | Current state | Likelihood | Impact | Risk | Rating |
|---|---|---|---|---|---|---|---|
| 1 | Sensitive data access | Data Protection | Mostly restricted, but rarely reviewed | 2 | 5 | 10 | **Medium** |
| 2 | Restore testing | Backups & Recovery | Tested once in the last year | 2 | 4 | 8 | **Medium** |
| 3 | Incident response plan | Incident Response | Written, but never practiced | 2 | 4 | 8 | **Medium** |
| 4 | End-of-life software | Patching & Vulnerability Management | One or two systems, with a replacement planned | 2 | 4 | 8 | **Medium** |
| 5 | Phishing simulations | Security Awareness Training | Once or twice a year | 2 | 3 | 6 | **Medium** |

## Remediation plan

### Next (30-90 days): risk index 6.8 → 4.4

| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |
|---|---|---|---|---|---|---|
| 1 | Restore testing | Run a test restore of one critical system every six months and record how long it takes. | Many businesses only discover their backups are broken in the middle of an emergency. | Low | $ | −4 |
| 2 | Phishing simulations | Run quarterly phishing simulations and track the click and report rates over time. | Practice makes phishing recognition a habit, and the results show where extra training is needed. | Low | $ | −3 |

### Later (90+ days): risk index 4.4 → 0

| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |
|---|---|---|---|---|---|---|
| 3 | Sensitive data access | Restrict sensitive folders and systems to the roles that need them, and review who has access twice a year. | Limiting access reduces how much data one compromised account or careless mistake can expose. | Medium | $ | −5 |
| 4 | Incident response plan | Write a two-page incident response plan covering who decides, who to call, and first steps, then walk through it once a year. | Decisions made calmly in advance are faster and better than decisions made mid-crisis. | Medium | $ | −4 |
| 5 | End-of-life software | Identify all end-of-life systems and budget to replace or isolate them within the next year. | Unsupported software no longer receives security fixes, so every new vulnerability stays open permanently. | High | $$$ | −4 |

## Method

Each control is scored 0-3 for maturity. Likelihood (1-5) comes from maturity; impact (1-5) is set per control and raised by 1 for data-related controls when sensitive data is held. Risk = likelihood × impact (1-25): Low 1-5, Medium 6-11, High 12-19, Critical 20-25. The risk index scales total risk from 0 (every control strong) to 100 (every control missing). Remediation items are ranked by risk reduction divided by effort.
