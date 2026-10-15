# Chronova Project — Status (as of 2026-10-15 11:27 IST)

**Project on hold per user decision (2026-10-15).** This document captures the current state so any future session can resume.

## Repo

- URL: https://github.com/venkat-narasimha/chronova
- Branch: main
- HEAD: 6c3ef22 (11 commits, all pushed)
- 23 files, ~1.5 MB
- Working tree: clean

## What's done

### Client intake templates (3 of 12, prospect-ready)
- `templates/A1-org-profile.md`
- `templates/A6-leave-policy.md`
- `templates/A7-approval-matrix.md`

### Internal playbook (1)
- `playbooks/B1-discovery-questionnaire.md`

### Migration tooling
- `scripts/migrate_tenant_data.py` — 1,138 lines, tenant-agnostic, idempotent
- `scripts/example/` — 11 CSVs + tenant_config.json (fictional "Greenwood MCH")

### Architecture reference (kept minimal)
- `docs/architecture/01-stock-frappe-hr-vs-custom.md` — single comparison view
- `docs/architecture/overview.mmd` — single high-level Mermaid diagram
- `docs/HOW-TO-ADD-A-NEW-CLIENT.md` — 8-step onboarding runbook

### Project meta
- `README.md`, `.gitignore`

## What's pending (not done)

### User decisions on A6/A7 fixes (D-α/D-β/D-γ) — NOT YET CONFIRMED
- D-α: L4 Chairman default threshold (currently ₹1,00,000)
- D-β: "Approval level" semantic (currently "Final authority")
- D-γ: SLA unit (currently Business Days)

### Deliberately deferred (per user "standard project")
- 9 missing intake templates (A2-A5 covered by CSVs; A8-A12 deferred to Phase 2)
- All SaaS-level analysis (cost, domain, multi-tenant Q1-Q4) — removed in cleanup
- All form-code metadata (Form Code, Version, Owner, Date, Format, etc.) — removed in 4 rounds

### Open (user action required)
- ₹ amounts in A6/A7: ₹25L IT exemption, ₹1,00,000 L4 threshold (user said "review" but did not request removal)
- Biometric device integration (Phase 5) — never tested
- Actual Frappe app code (`apps/chronova/`) — not built
- Pilot college — not named
- Real prospect deployment — not started

## How to resume (next session)

1. Open `STATUS.md` (this file)
2. Read workspace `memory/2026-10-15.md` for full session context
3. Check `LEARNINGS.md` for new lessons (added #188, #189, #190, #191 today)
4. Confirm with user before resuming any work
5. User's last-stated next move: build the actual Frappe app (Option A from 11:21 IST)

## Origin context

Based on the Haritha Hospitals deployment (2026-08-29 to 2026-10-01). ~99% of the 282 Haritha customizations are reusable across colleges. Chronova = the reusable SaaS product layer, built 2026-10-15 in ~45 minutes, then cleaned up to "standard project" structure, then placed on hold.
