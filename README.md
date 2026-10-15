# Chronova

Reusable Frappe HR setup for colleges, universities, and hospitals.

## What's in this repo

- `templates/` — client intake forms (A1 org profile, A6 leave policy, A7 approval matrix)
- `playbooks/` — internal scripts (B1 discovery questionnaire)
- `scripts/` — migration tooling (`migrate_tenant_data.py`) + example data
- `docs/architecture/` — architecture reference

## How to use

1. New prospect fills `templates/A1`, `templates/A6`, `templates/A7`
2. Consultant copies `scripts/example/` to a new data folder
3. Consultant edits the CSVs from the prospect's answers
4. Run `python scripts/migrate_tenant_data.py --tenant-config <path> --data-dir <path> --site <site>`
5. Verify in the live Frappe HR instance

See `scripts/example/README.md` for schema details and `playbooks/B1-discovery-questionnaire.md` for the prospect meeting script.

## Status

v0.1. Prospect-ready intake templates. Migration script tested statically.

## Origin

Based on the Haritha Hospitals deployment (2026-08-29), with the per-tenant data layer abstracted for reuse across colleges and hospitals.
