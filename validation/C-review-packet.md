# C — Architecture Review Packet (1-hour working session)

**Date:** 2026-10-15
**For:** Venkat Narasimha (Founder, College HR Foundation)
**Goal:** Run a focused 1-hour working session to lock the open architectural decisions before first pilot college.
**Format:** Print this page. Bring it + a pen.

---

## What this is
A scannable summary of the 4 architecture docs + a 1-hour agenda + the 7 open decisions Venkat must answer to move from "first-draft architecture" to "pilot-ready SaaS". Designed to be readable in 5 minutes and actionable in 60.

## Who reads it
- **Venkat** (only) — runs the session solo or with the dev lead

---

## 1. The 4 architecture docs — at a glance

| # | Doc | What it covers | Who reads it | "If you only read 1 sentence" |
|---|---|---|---|---|
| 01 | **Stock Frappe HR vs Custom (Haritha → Foundation)** | 282-row comparison: what Frappe HR gives free (5 modules, 5 stock workflows missing) vs. what Haritha added (78 CFs, 189 PSs, 1 custom DocType, 2 workflows, 6 role profiles, 858 perms) vs. what's reusable (99%) vs. Haritha-only (1 `is_emergency` CF + letterhead). | Venkat (sales pitch), sales engineer, new dev | **"99% of Haritha's 282 customizations are reusable across colleges — the SaaS thesis is data, not code."** |
| 02 | **Multi-Tenant Architecture (SaaS model)** | Why we chose shared-DB with `company` field (vs. one-DB-per-tenant), 6× cost advantage at 20 tenants, RBAC scope already in place, when we'd revisit (regulator / 30+ tenants). | Venkat, sales, dev/SRE, future legal | **"Shared DB with `company` field — 6× cheaper at 20 tenants, but revisit at 30+ tenants or for any college requiring physical isolation."** |
| 03 | **Data Flow: Discovery → Live (9-phase methodology)** | The 9-phase onboarding: 0-Sales → 1-Discovery → 2-Contract → 3-Org+Shift+Leave Config → 4-Employee Lifecycle → 5-Biometric → 6-Workflows+Roles → 7-UAT+Training → 8-Go-Live → 9-Steady-State. Per-phase input/activity/output/templates/time. | Sales engineer, implementation engineer, Venkat, client HR Head | **"6-10 weeks elapsed, 150-200 engineering hours — that's the SOW unit of work for one college."** |
| MMD | **architecture-overview.mmd** (single Mermaid) | One-page visual: 5 stock HRMS modules → 78 reusable CFs + 189 PSs + 6 RPs + 2 WFs → per-tenant config → 4 example tenants (Haritha + ABC + XYZ + DEF) → end users. | Sales decks, Notion, partner intros | **"The picture: stock Frappe + custom app layer + per-tenant config = 4 colleges, one codebase, isolated data."** |

---

## 2. Top 7 open decisions Venkat must make

For each: the question, the 2-3 options, and my (Agent 4) recommendation in **bold**.

| # | Decision | Options | **Recommendation** | Why |
|---|---|---|---|---|
| **Q1** | **Tenancy model** | (a) Shared DB + `company` field (chosen in Doc 02) · (b) One DB per tenant · (c) One schema per tenant | **(a) — sign off on Doc 02's choice** | 6× cost advantage at scale; RBAC already scoped; revisit at 30+ tenants. **Just lock it.** |
| **Q2** | **App name + spelling** | (a) `college_hr_foundation` · (b) `processbricks_hr` · (c) keep `haritha_hospital` (rebrand later) | **(a) `college_hr_foundation`** | Clearer for sales; matches product name. Decide now because role-profile prefix (`CHRF:` vs `Haritha:`) follows. |
| **Q3** | **SaaS domain** | (a) `college-hr-foundation.com` · (b) `processbricks.io/hr` · (c) `chrf.in` | **(a) — clean, brandable, matches name** | Decide before Step 2.3 (role-profile prefix) and Step 2.7 (custom image tag). |
| **Q4** | **First-pilot college** | (a) Friendly contact in network · (b) Wait for inbound RFP · (c) Self-pilot (fake data) | **(a) — pick a friendly contact** | Without a real pilot, all docs remain theoretical. The 6-10 week timeline is the proof. |
| **Q5** | **SLA numbers** | (a) 99.5% uptime / 6h RPO / 24h RTO / IST business hours · (b) 99.9% / 1h RPO / 4h RTO / 24×7 · (c) Best-effort (no SLA) | **(a) for v1, escalate to (b) at 5+ tenants** | (b) costs 2× the SRE time. (c) loses enterprise deals. (a) is the realistic starting point. |
| **Q6** | **`tenant_seed.py` ownership** | (a) Venkat writes it (he wrote Haritha's `migrate_master_data.py`) · (b) Hire a dev · (c) Outsource to Frappe partner | **(b) — hire a dev (50% time, 4 months)** | Venkat is the founder, not the dev. (a) is 4 months of his time. (c) is expensive and slow. |
| **Q7** | **Per-tenant backup strategy** | (a) `mysqldump --where='company=...'` (script-it-yourself) · (b) Frappe's built-in backup + manual filter · (c) Third-party (e.g., Percona XtraBackup) | **(a) for v1, (c) at 10+ tenants** | (a) is 3 days of dev work and reuses the cron. (c) is overkill until scale. |

---

## 3. Suggested 1-hour agenda

| Time | Activity | Output |
|---|---|---|
| **0:00 – 0:05** | Orient. Read the "1-sentence" takeaways from §1 above. Skim the 4 doc titles. | Mental model loaded |
| **0:05 – 0:15** | **Doc 01 review** (Stock vs Custom). Confirm: is the "99% reusable" headline believable? Are the 6 Haritha-specific items correctly identified? | Sign-off or list of 1-2 corrections |
| **0:15 – 0:30** | **Doc 02 review** (Multi-tenant). Lock Q1 (tenancy) and Q3 (domain). Note any regulator-driven concerns. | Q1, Q3 answered |
| **0:30 – 0:45** | **Doc 03 review** (9-phase flow). Lock Q4 (pilot), Q5 (SLA numbers), Q6 (who builds `tenant_seed.py`). | Q4, Q5, Q6 answered |
| **0:45 – 0:55** | **Doc MMD review** (architecture overview). Lock Q2 (app name) and Q7 (backup strategy). Sanity-check the visual for the sales deck. | Q2, Q7 answered; visual approved |
| **0:55 – 1:00** | **Action items.** Write down: who does what by when. Send this packet's "Decisions to lock" list to the dev. | 3-5 action items with owners + dates |

---

## 4. Decisions to lock (the "must answer" list)

These 7 questions must be answered for the architecture to be **pilot-ready** (i.e., the dev can start Step 2 of Doc 02's migration path):

| # | Question | Answer (fill in during session) |
|---|---|---|
| Q1 | Tenancy: shared-DB with `company` field — **approve Doc 02's recommendation?** | YES / NO / DEFER |
| Q2 | App name: `college_hr_foundation` — **approve?** | YES / NO (alt: ________) |
| Q3 | SaaS domain: `college-hr-foundation.com` — **approve?** | YES / NO (alt: ________) |
| Q4 | First pilot: **name the friendly contact + expected kickoff date** | Name: ________  Date: ________ |
| Q5 | SLA numbers (v1): 99.5% uptime / 6h RPO / 24h RTO / IST business hours — **approve?** | YES / NO (alt: ________) |
| Q6 | Dev resource: hire 50%-time dev for 4 months — **approve budget?** | YES / NO (alt: ________) |
| Q7 | Backup strategy: `mysqldump --where='company=...'` (script-it-yourself) — **approve v1 approach?** | YES / NO (alt: ________) |

---

## 5. Open questions to defer (do NOT answer in this session)

These are tempting but **out of scope for the architecture review** — capture them as a follow-up backlog, not as session decisions:

- Pricing per-tenant-per-month (commercial decision, not architectural)
- Ticketing system (osTicket vs Zammad vs Freshdesk) — Doc 03 mentions this is a Phase 9 decision
- Training video tool (Notion / Loom / Google Slides) — Doc 03 next steps #6
- DPDP Act 2023 compliance review (legal decision, not architectural)
- Whether to extract Haritha's 14,030 lines of docs into reusable templates (Doc 03 next steps #1)

---

## 6. After the session — what to send to the dev

A 3-line email is enough:

```
Subject: College HR Foundation — architecture decisions (2026-10-15)

Dev,

Architecture review done. Decisions:
- Tenancy: shared-DB + company field (Doc 02 confirmed)
- App name: college_hr_foundation (CHRF prefix)
- Backup: mysqldump --where='company=...'

You can start Step 2 of Doc 02's migration path. Ping me on
[domain decision] and [pilot college name] when you have them.

— Venkat
```

---

*See also: `A-verification.md` (B1 defaults — all 3 ✅ applied), `B-spot-check.md` (A6/A7 spot-check — 28 findings, 8 HIGH).*
