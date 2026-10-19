# Cyber Risk Assessment: Larkspur Family Dental

*Healthcare (dental practice) · 14 employees · Handles sensitive data · Generated 2026-10-19*

> Fictional organization, created to demonstrate the assessment tool.

## Executive summary

Larkspur Family Dental is at high risk. Overall security maturity is 19.8% and the risk index is 85.1 out of 100. All 18 controls reviewed have gaps, including 10 rated Critical and 8 rated High. The weakest areas are Security Awareness Training (11.1%) and Access Control (16.7%). There are 10 quick wins that can be completed in the next 30 days at low cost. Doing them lowers the risk index from 85.1 to 39.9, a reduction of 45.2 points. Completing the full plan brings the risk index down to 0.

| Overall maturity | Risk index | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| 19.8% | 85.1 / 100 | 10 | 8 | 0 | 0 |

## Maturity by control area

| Area | NIST CSF 2.0 | Maturity | | Gaps | Worst rating |
|---|---|---|---|---|---|
| Security Awareness Training | PR.AT | 11.1% | `██░░░░░░░░░░░░░░░░░░` | 3 | Critical |
| Access Control | PR.AA | 16.7% | `███░░░░░░░░░░░░░░░░░` | 4 | Critical |
| Incident Response | RS.MA | 16.7% | `███░░░░░░░░░░░░░░░░░` | 2 | Critical |
| Data Protection | PR.DS | 16.7% | `███░░░░░░░░░░░░░░░░░` | 2 | Critical |
| Backups & Recovery | PR.DS / RC.RP | 22.2% | `████░░░░░░░░░░░░░░░░` | 3 | Critical |
| Patching & Vulnerability Management | PR.PS / ID.RA | 25% | `█████░░░░░░░░░░░░░░░` | 4 | High |

## Top risks

| # | Control | Area | Current state | Likelihood | Impact | Risk | Rating |
|---|---|---|---|---|---|---|---|
| 1 | Sensitive data access | Data Protection | Everyone can access everything | 5 | 5 | 25 | **Critical** |
| 2 | Multi-factor authentication | Access Control | Only on a few accounts or optional | 4 | 5 | 20 | **Critical** |
| 3 | Admin rights | Access Control | Everyone is an administrator | 5 | 4 | 20 | **Critical** |
| 4 | Account offboarding | Access Control | Eventually, when someone remembers | 4 | 5 | 20 | **Critical** |
| 5 | Backup frequency | Backups & Recovery | Monthly or manually when someone remembers | 4 | 5 | 20 | **Critical** |

## Remediation plan

### Now (0-30 days): risk index 85.1 → 39.9

| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |
|---|---|---|---|---|---|---|
| 1 | Restore testing | Run a test restore of one critical system every six months and record how long it takes. | Many businesses only discover their backups are broken in the middle of an emergency. | Low | $ | −16 |
| 2 | Security training | Require short security training for every new hire and an annual refresher for all staff. | Most breaches start with a person being tricked. Trained staff spot and report attacks earlier. | Low | $ | −16 |
| 3 | Multi-factor authentication | Turn on MFA for every user's email and remote access, starting with admin accounts. | Stolen passwords are the most common way attackers get in. MFA stops most of those attempts even when the password is known. | Low | $ | −15 |
| 4 | Account offboarding | Create an offboarding checklist that disables all accounts on the employee's last day, and review active accounts quarterly. | Former employees' accounts are an open door. Nobody notices when they're misused. | Low | $ | −15 |
| 5 | Device encryption | Turn on built-in full-disk encryption (BitLocker or FileVault) on every laptop and enforce it centrally. | A lost or stolen laptop without encryption is a data breach. With encryption, it's just a lost device. | Low | $ | −15 |
| 6 | Emergency contacts | Keep a printed and offline list of emergency contacts: IT support, cyber insurer, legal counsel, and key vendors. | During an attack, email and shared drives may be unavailable exactly when the contacts are needed. | Low | $ | −12 |
| 7 | Software updates | Turn on automatic updates for all computers and apply critical security patches within 14 days. | Attackers exploit known vulnerabilities within days of a patch being released. Unpatched systems are the easiest targets. | Low | $ | −12 |
| 8 | Password management | Roll out a company password manager and require unique passwords for every system. | Reused or shared passwords mean one breach anywhere unlocks accounts everywhere. | Low | $ | −12 |
| 9 | Phishing simulations | Run quarterly phishing simulations and track the click and report rates over time. | Practice makes phishing recognition a habit, and the results show where extra training is needed. | Low | $ | −12 |
| 10 | Incident reporting channel | Set up one clear reporting channel, such as a report-phishing button or a security email address, and announce it to all staff. | Fast reporting shortens how long an attacker has before they're stopped. | Low | $ | −9 |

### Next (30-90 days): risk index 39.9 → 0

| # | Control | Action | Why it matters | Effort | Cost | Risk ↓ |
|---|---|---|---|---|---|---|
| 11 | Sensitive data access | Restrict sensitive folders and systems to the roles that need them, and review who has access twice a year. | Limiting access reduces how much data one compromised account or careless mistake can expose. | Medium | $ | −20 |
| 12 | Admin rights | Remove local admin rights from everyday accounts and give IT separate admin logins. | When a user with admin rights clicks a malicious link, the attacker gets full control of the computer. | Medium | $ | −16 |
| 13 | Incident response plan | Write a two-page incident response plan covering who decides, who to call, and first steps, then walk through it once a year. | Decisions made calmly in advance are faster and better than decisions made mid-crisis. | Medium | $ | −16 |
| 14 | Backup frequency | Set up automatic daily backups of all critical systems and shared files. | Without recent backups, ransomware or a failed drive can mean permanent loss of records and days of downtime. | Medium | $$ | −15 |
| 15 | Offline / immutable backups | Keep at least one backup copy offline or in immutable cloud storage that ordinary accounts can't delete. | Ransomware deliberately looks for connected backups and encrypts them too. A separate copy is what makes recovery possible. | Medium | $$ | −15 |
| 16 | Endpoint protection | Deploy managed endpoint protection on every device, with alerts sent to IT or your service provider. | Endpoint protection catches and blocks most common malware before it spreads. | Medium | $$ | −12 |
| 17 | Asset inventory | Build a simple inventory of every device and key application, with its owner, and review it quarterly. | You can't patch, back up, or protect what you don't know you have. | Medium | $ | −12 |
| 18 | End-of-life software | Identify all end-of-life systems and budget to replace or isolate them within the next year. | Unsupported software no longer receives security fixes, so every new vulnerability stays open permanently. | High | $$$ | −12 |

## Method

Each control is scored 0-3 for maturity. Likelihood (1-5) comes from maturity; impact (1-5) is set per control and raised by 1 for data-related controls when sensitive data is held. Risk = likelihood × impact (1-25): Low 1-5, Medium 6-11, High 12-19, Critical 20-25. The risk index scales total risk from 0 (every control strong) to 100 (every control missing). Remediation items are ranked by risk reduction divided by effort.
