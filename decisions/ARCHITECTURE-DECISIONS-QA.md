# Chronova — Architecture Decisions Q&A Worksheet

**Date:** 2026-10-15
**For:** Venkat Narasimha (Founder)
**Use:** Print this page. Bring it + a pen to your 1-hour working session.
**Goal:** Lock the 4 open architecture decisions that block the multi-tenant (Phase A SaaS) work.

**How to use:** For each question, read the context and options, glance at the recommendation, then fill in the "Decision" block at the bottom of that question. End with the "Decisions to Lock" summary at the end.

---

## Q1 — Tenancy Model  (OPEN — needs decision)

**Context.** Today the custom app ships with 282 fixture rows. Each Chronova tenant is one college (or college + hospital). The question: do all tenants share one MariaDB and partition by the `company` field, or does each tenant get its own MariaDB? Source: `docs/architecture/02-multi-tenant-architecture.md`.

**Options.**

| # | Option | Cost @ 20 tenants | Isolation | Ops complexity | Per-tenant backup |
|---|---|---|---|---|---|
| A | **Shared DB, `company` field partition** | ~$60/mo | Logical (row-level) | Low — 1 stack | `mysqldump --where='company=...'` |
| B | **One DB per tenant** | ~$400/mo | Physical (separate DB) | High — N stacks | Trivial — dump single DB |

**Key trade-offs.**

| # | Trade-off | Shared DB (A) | One DB per tenant (B) |
|---|---|---|---|
| 1 | HRMS native support | First-class (`company` is built-in everywhere) | Each tenant reinstalls Frappe HR |
| 2 | `bench update` + `bench migrate` | Once for all tenants | Run N times (or orchestrate) |
| 3 | Cross-tenant analytics (your future sales-engineering data) | Trivial (single query) | Cross-DB UNIONs (painful) |
| 4 | Regulator demands physical isolation (govt/defense) | Cannot satisfy without split | Trivial to satisfy |
| 5 | When to revisit | At ~30 tenants OR physical-isolation demand | n/a — already there |

**Recommendation: Option A** (shared DB). Frappe HR treats `company` as a first-class field on Employee, Department, Shift Type, Leave Allocation, Attendance — isolation at the application layer is mostly free, and the 6-7x cost gap matters in early-stage SaaS. Migrate to B later only if a paying customer demands physical isolation.

**Decision Q1 (circle one):**  A (shared DB)  /  B (one DB per tenant)  /  DEFER
Notes: ____________________________   Initial: ____   Date: ______

---

## Q2 — App Name  (RESOLVED — confirm in writing)

**Locked decision (today, 2026-10-15):** **Chronova** (replaces "college-hr-foundation" and the misspelled "haritha_hospital").

- Python module name: `chronova` (lowercase, no spaces, no hyphens)
- Git remote: `git@github.com:venkat-narasimha/chronova.git`
- Role-profile prefix will become `Chronova:` (downstream of app rename)
- Docker image tag: `frappe/custom_apps:college-hr-v1` (image tag unchanged for v1)

**Why now.** Affects Step 2.3 (role-profile prefix) and Step 2.7 (custom image tag) of the migration path. Locking it now means the dev can proceed without re-work.

**Confirmation Q2 (just initial):**  Confirmed: Chronova  /  NOT confirmed (alt: __________)
Initial: ____   Date: ______

---

## Q3 — SaaS Domain  (PARTIALLY OPEN — name picked, TLD not yet bought)

**Context.** The container has no `whois` so availability + price must be checked from your laptop (or a registrar like namecheap.com / porkbun.com / godaddy.com).

**Options to evaluate.**

| TLD | Typical ₹/yr (approx) | Position |
|---|---|---|
| chronova.in | ~600-900 | India-first customers; cheaper; usually more name availability |
| chronova.com | ~900-1500 | Global standard; expected by enterprise buyers; may be taken |
| chronova.io | ~3000-4500 | SaaS-style ("startup / tech" signal); pricier |
| chronova.co | ~1500-2500 | Short, brandable; less recognized as a TLD |
| chronova.app | ~1000-1500 | App/SaaS signal; more niche; less trusted for HR data |

**Recommendation: `chronova.in`** for v1. India-first customer base, cheapest, and the .in namespace is much less saturated so the name is almost certainly available. You can buy .com later as a redirect (most registrars support 301 redirect from .com -> .in for ~₹900/yr extra). If you want the global-enterprise signal from day 1 and budget allows, take .com.

**Action for Venkat (run on your laptop):**

```
whois chronova.in       # or visit https://www.namecheap.com and search "chronova"
```

If `chronova.in` is available and you like the price, reply with **"buy .in"** and the dev proceeds with that domain. If you want to check `.com` first, reply with **"try .com"** and we'll loop back after.

**Decision Q3 (circle one):**  chronova.in  /  chronova.com  /  chronova.io  /  chronova.co  /  chronova.app  /  DEFER
Notes: ____________________________   Initial: ____   Date: ______

---

## Q4 — Friendly Pilot Contact  (OPEN — needs Venkat to name)

**Context.** Without a real pilot college, every multi-tenant doc (this one included) is theoretical. The 9-phase methodology (`docs/architecture/03-data-flow-discovery-to-live.md`) and the 6-10 week timeline are still unproven. A friendly pilot turns the architecture into a paying reality and gives you real numbers to put in your next sales pitch.

**Pilot criteria — a good first college checks most of these boxes:**

| # | Criterion | Check |
|---|---|---|
| 1 | Friendly principal / HR Head who knows you and is willing to be a "learning case" (forgives rough edges) | [ ] |
| 2 | Decent in-house IT or a managed-IT partner (someone who can unblock a network or server issue in hours, not days) | [ ] |
| 3 | 50-250 employees (small enough to onboard in 6-10 weeks, big enough to exercise shift/leave workflows) | [ ] |
| 4 | Willing to be a public reference / case study (post-go-live, after a 90-day settling period) | [ ] |
| 5 | Has biometric or will adopt one (so we exercise the Phase 5 integration in the pilot) | [ ] |

**Fill in your pick (or shortlist 1-2 candidates):**

| Field | Value |
|---|---|
| (a) Contact name + role | __________________________________________ |
| (b) Institution name + type (engineering / arts / medical / etc.) | __________________________________________ |
| (c) Why friendly? (history, prior contact, family tie, mutual friend) | __________________________________________ |
| (d) Rough size: employees ____ / students ____ / branches ____ | __________________________________________ |
| (e) Target go-live quarter (e.g., Q1-2027) | __________________________________________ |
| (f) Backup contact (in case (a) is unavailable) | __________________________________________ |

**Decision Q4 (circle one):**  Named above, proceed with outreach  /  Need more time, defer 30 days
Notes: ____________________________   Initial: ____   Date: ______

---

## Decisions to Lock — Summary (fill in at the end of the session)

| # | Question | Answer (the "locked" version) |
|---|---|---|
| Q1 | Tenancy model | A (shared DB) / B (one DB per tenant) / DEFER |
| Q2 | App name | Chronova (confirmed) / alt: _______ |
| Q3 | SaaS domain | chronova._____ (TLD) |
| Q4 | Pilot contact | Name: _______________  Go-live: Q__-20__ |

**Session notes / blockers / follow-ups:**
_________________________________________________________
_________________________________________________________
_________________________________________________________

**Next step after session:** email the 4 locked answers to the dev so Step 2 of the migration path can start.

---

*See also: `validation/C-review-packet.md` (full review packet, 7-question set); `docs/architecture/02-multi-tenant-architecture.md` (Q1 source); `docs/architecture/01-stock-frappe-hr-vs-custom.md` (Q4 context); `docs/architecture/03-data-flow-discovery-to-live.md` (full methodology).*
