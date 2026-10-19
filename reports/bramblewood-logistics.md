# Cyber Risk Assessment: Bramblewood Logistics

*Transportation & warehousing · 48 employees · No sensitive data flagged · Generated 2026-10-19*

> Fictional organization, created to demonstrate the assessment tool.

## Executive summary

Bramblewood Logistics is at moderate risk. Overall security maturity is 60% and the risk index is 36.8 out of 100. 17 of 18 controls reviewed have gaps, including 5 rated High. The weakest areas are Incident Response (50%) and Security Awareness Training (55.6%). There are 2 quick wins that can be completed in the next 30 days at low cost. Doing them lowers the risk index from 36.8 to 29.3, a reduction of 7.5 points. Completing the full plan brings the risk index down to 0.

| Overall maturity | Risk index | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| 60% | 36.8 / 100 | 0 | 5 | 12 | 1 |

## Maturity by control area

| Area | NIST CSF 2.0 | Maturity | | Gaps | Worst rating |
|---|---|---|---|---|---|
| Incident Response | RS.MA | 50% | `██████████░░░░░░░░░░` | 2 | High |
| Security Awareness Training | PR.AT | 55.6% | `███████████░░░░░░░░░` | 3 | High |
| Access Control | PR.AA | 58.3% | `████████████░░░░░░░░` | 4 | High |
| Patching & Vulnerability Management | PR.PS / ID.RA | 58.3% | `████████████░░░░░░░░` | 4 | High |
| Backups & Recovery | PR.DS / RC.RP | 66.7% | `█████████████░░░░░░░` | 2 | High |
| Data Protection | PR.DS | 66.7% | `█████████████░░░░░░░` | 2 | Medium |

## Top risks

| # | Control | Area | Current state | Likelihood | Impact | Risk | Rating |
|---|---|---|---|---|---|---|---|
| 1 | Admin rights | Access Control | Many users have admin rights | 4 | 4 | 16 | **High** |
| 2 | Restore testing | Backups & Recovery | Never formally tested | 4 | 4 | 16 | **High** |
| 3 | Incident response plan | Incident Response | Informal: people would figure it out | 4 | 4 | 16 | **High** |
| 4 | End-of-life software | Patching & Vulnerability Management | Several systems, with no replacement plan | 4 | 4 | 16 | **High** |
| 5 | Phishing simulations | Security Awareness Training | Tried once | 4 | 3 | 12 | **High** |

## Remediation plan

### Now (0-30 days): risk index 36.8 → 29.3

| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |
|---|---|---|---|---|---|---|
| 1 | Restore testing | Run a test restore of one critical system every six months and record how long it takes. | Many businesses only discover their backups are broken in the middle of an emergency. | Low | $ | −12 |
| 2 | Phishing simulations | Run quarterly phishing simulations and track the click and report rates over time. | Practice makes phishing recognition a habit, and the results show where extra training is needed. | Low | $ | −9 |

### Next (30-90 days): risk index 29.3 → 5.7

| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |
|---|---|---|---|---|---|---|
| 3 | Admin rights | Remove local admin rights from everyday accounts and give IT separate admin logins. | When a user with admin rights clicks a malicious link, the attacker gets full control of the computer. | Medium | $ | −12 |
| 4 | Incident response plan | Write a two-page incident response plan covering who decides, who to call, and first steps, then walk through it once a year. | Decisions made calmly in advance are faster and better than decisions made mid-crisis. | Medium | $ | −12 |
| 5 | Multi-factor authentication | Turn on MFA for every user's email and remote access, starting with admin accounts. | Stolen passwords are the most common way attackers get in. MFA stops most of those attempts even when the password is known. | Low | $ | −5 |
| 6 | End-of-life software | Identify all end-of-life systems and budget to replace or isolate them within the next year. | Unsupported software no longer receives security fixes, so every new vulnerability stays open permanently. | High | $$$ | −12 |
| 7 | Account offboarding | Create an offboarding checklist that disables all accounts on the employee's last day, and review active accounts quarterly. | Former employees' accounts are an open door. Nobody notices when they're misused. | Low | $ | −4 |
| 8 | Device encryption | Turn on built-in full-disk encryption (BitLocker or FileVault) on every laptop and enforce it centrally. | A lost or stolen laptop without encryption is a data breach. With encryption, it's just a lost device. | Low | $ | −4 |
| 9 | Software updates | Turn on automatic updates for all computers and apply critical security patches within 14 days. | Attackers exploit known vulnerabilities within days of a patch being released. Unpatched systems are the easiest targets. | Low | $ | −4 |
| 10 | Security training | Require short security training for every new hire and an annual refresher for all staff. | Most breaches start with a person being tricked. Trained staff spot and report attacks earlier. | Low | $ | −4 |
| 11 | Password management | Roll out a company password manager and require unique passwords for every system. | Reused or shared passwords mean one breach anywhere unlocks accounts everywhere. | Low | $ | −3 |
| 12 | Emergency contacts | Keep a printed and offline list of emergency contacts: IT support, cyber insurer, legal counsel, and key vendors. | During an attack, email and shared drives may be unavailable exactly when the contacts are needed. | Low | $ | −3 |
| 13 | Incident reporting channel | Set up one clear reporting channel, such as a report-phishing button or a security email address, and announce it to all staff. | Fast reporting shortens how long an attacker has before they're stopped. | Low | $ | −3 |

### Later (90+ days): risk index 5.7 → 0

| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |
|---|---|---|---|---|---|---|
| 14 | Offline / immutable backups | Keep at least one backup copy offline or in immutable cloud storage that ordinary accounts can't delete. | Ransomware deliberately looks for connected backups and encrypts them too. A separate copy is what makes recovery possible. | Medium | $$ | −5 |
| 15 | Sensitive data access | Restrict sensitive folders and systems to the roles that need them, and review who has access twice a year. | Limiting access reduces how much data one compromised account or careless mistake can expose. | Medium | $ | −4 |
| 16 | Endpoint protection | Deploy managed endpoint protection on every device, with alerts sent to IT or your service provider. | Endpoint protection catches and blocks most common malware before it spreads. | Medium | $$ | −4 |
| 17 | Asset inventory | Build a simple inventory of every device and key application, with its owner, and review it quarterly. | You can't patch, back up, or protect what you don't know you have. | Medium | $ | −3 |

## Method

Each control is scored 0-3 for maturity. Likelihood (1-5) comes from maturity; impact (1-5) is set per control and raised by 1 for data-related controls when sensitive data is held. Risk = likelihood × impact (1-25): Low 1-5, Medium 6-11, High 12-19, Critical 20-25. The risk index scales total risk from 0 (every control strong) to 100 (every control missing). Remediation items are ranked by risk reduction divided by effort.
