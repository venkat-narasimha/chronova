# How to onboard a new prospect using this template

This directory is a **cloneable skeleton** for any new Chronova tenant. It
pre-bakes the 4 architecture decisions that were locked on 2026-10-15
(see `decisions/ARCHITECTURE-DECISIONS-QA.md`) so every new prospect
starts from a consistent baseline. The concrete reference example
(Greenwood MCH) lives in `../migrate_tenant_data.example/` — DO NOT edit
that one, it is canonical.

## Onboarding steps

1. **Clone the template.** Pick a short, kebab-case slug for the
   prospect and copy the directory.

   ```bash
   cp -r migrate_tenant_data.template/  data/stmarys-engineering/
   cd data/stmarys-engineering/
   ```

   The slug becomes the prospect's data folder name everywhere
   (backups, restore scripts, dashboard URLs). Lowercase, hyphens only,
   no spaces, ≤32 chars.

2. **Edit `tenant_config.json`** — fill the required and prospect-specific
   fields. See the `_metadata._placeholders` block in the file for
   guidance. Minimum required: `company_name` + `company_abbr`. The
   `_metadata` block is ignored by `migrate_tenant_data.py` (the script
   reads only the documented top-level keys) so you can leave it in
   place or strip it once you no longer need the inline docs.

3. **Fill the CSVs from A1 / A6 / A7.** Copy the A1-org-profile.md,
   A6-leave-policy.md, A7-approval-matrix.md outputs from
   `templates/` into this folder as `company.csv`, `department.csv`,
   `designation.csv`, `employee.csv`, `shift_type.csv`,
   `holiday_list.csv`, `holidays.csv`, `leave_type.csv`,
   `leave_policy.csv`, `leave_policy_detail.csv`,
   `shift_assignment.csv` (plus `gender.csv` / `employment_type.csv` /
   `shift_location.csv` if applicable). See
   `../migrate_tenant_data.example/README.md` for the exact column
   schema of each CSV.

4. **Dry-run first.** Validate the CSVs + config against the live Frappe
   HR site without writing anything.

   ```bash
   python migrate_tenant_data.py \
       --tenant-config data/stmarys-engineering/tenant_config.json \
       --data-dir      data/stmarys-engineering/ \
       --site          stmarys.chronova.in \
       --dry-run
   ```

   Read the `=== SUMMARY ===` block. If `fail > 0` or `errors_sample`
   is non-empty, fix the offending CSV row(s) and re-run.

5. **Live-run.** Same command without `--dry-run`. The script
   idempotently upserts, so re-running is safe if a single DocType
   fails partway (it commits per-DocType, see
   `migrate_tenant_data.py` line "partial progress is committed per
   DocType").

   ```bash
   python migrate_tenant_data.py \
       --tenant-config data/stmarys-engineering/tenant_config.json \
       --data-dir      data/stmarys-engineering/ \
       --site          stmarys.chronova.in
   ```

6. **Verify in the live UI.** See "Sanity checks after first migration"
   below for the 4-5 things to click through.

7. **Commit the prospect's data folder to its own Git repo** (or a
   `data/` subfolder in the main chronova repo, per your git policy).
   This gives you a per-prospect audit trail of every config change.

8. **Update `decisions/ARCHITECTURE-DECISIONS-QA.md` Q4** when the
   first prospect is signed and onboarded — note the actual pilot
   institution name, contact, and go-live quarter.

---

## How each Q1-Q4 decision is encoded, and what to do if the prospect wants a different answer

### Q1 — Tenancy model

- **Field:** `_metadata._architecture_decisions.Q1_tenancy_model.value`
  (also implicit in the `tenancy_model: "shared_db_company_partition"`
  plan; the actual config file does NOT carry a tenancy field because
  the live MariaDB is provisioned once for the whole multi-tenant
  stack).
- **Default value:** `shared_db_company_partition` (Option A).
- **What this means operationally:** the prospect's `company` row lives
  in the shared Chronova MariaDB, and every employee/department/shift
  is partitioned by `company` Link field. ~$60/mo at 20 tenants.
- **If the prospect wants per-tenant DB (Option B) instead:** this is a
  **stack-level change**, not a config change. Provision a new
  MariaDB container, a new Frappe bench, and migrate the prospect's
  rows into it. Coordinate with the platform owner; do NOT just edit
  `tenant_config.json`. The decision is locked for the v1 SaaS launch
  — only revisit at ~30 tenants or a paying customer demanding
  physical isolation (regulator/government/defense).

### Q2 — App name

- **Field:** `_metadata._architecture_decisions.Q2_app_name.value`.
- **Default value:** `chronova` (locked 2026-10-15, do not change).
- **What this means operationally:** the Python module under
  `apps/chronova/`, the Git remote `git@github.com:venkat-narasimha/chronova.git`,
  the role-profile prefix `Chronova:`, and the custom Docker image
  tag all use this name.
- **If a prospect wants a different app name:** they don't get to
  choose. The app is the platform; the prospect is a tenant. The
  locked value is correct for every prospect, full stop.

### Q3 — SaaS domain

- **Field:** `_metadata._architecture_decisions.Q3_saas_domain.value`.
- **Default value:** `chronova.in` (recommended, pending Venkat's
  working-session confirmation).
- **What this means operationally:** the Frappe site is served at
  `<prospect-slug>.chronova.in` (e.g. `stmarys.chronova.in`).
- **If the TLD changes** (e.g. Venkat decides on `chronova.com`):
  edit the `value` field above, update every prospect's `site` arg
  in their `run_migration.sh`, and re-provision the wildcard SSL cert
  for the new TLD. This is a 30-minute chore across all prospect
  folders, not a re-architecture.
- **If a prospect wants their own custom domain** (e.g.
  `hr.stmarys.edu.in`): that's a per-prospect CNAME, NOT a change
  to Q3. The Frappe site still lives at `stmarys.chronova.in`
  internally; the CNAME is a DNS-level redirect.

### Q4 — Pilot contact

- **Field:** `_metadata._architecture_decisions.Q4_pilot_company.value`
  and the per-prospect contact info in `company.csv` /
  `employee.csv` / `approver_user`.
- **Default value:** `"TODO"` (Venkat to name in the working session).
- **What this means operationally:** the FIRST prospect's tenant
  config carries the pilot's actual legal name + primary contact
  details so the welcome email, SOW, and case-study copy all read
  right.
- **If this is the first/pilot prospect:** fill the actual pilot
  college's name, contact, role, and target go-live quarter into the
  Q4 metadata block.
- **If this is a second-and-later prospect:** the Q4 field becomes
  just "the name of this prospect" — update the `notes` string in
  the Q4 metadata block to remove the "pilot" framing.

---

## Sanity checks after first migration

After the live-run completes successfully, click through these in the
Frappe HR UI to confirm the data landed:

1. **Company record.** Log in, search for the company by the
   `company_name` you set. Verify `abbr`, `country`, `default_currency`,
   `fiscal_year_start_month`, and `timezone` are all as expected.
2. **Department tree.** Open the Department list, group by
   `parent_department`, confirm the full hierarchy is there with no
   orphans and no duplicates. The `All Departments` root should
   exist exactly once.
3. **Employee list filter.** Open Employee, filter by
   `Company = <your-company>`. The row count should match your CSV
   row count (minus any rows the script marked `skipped`). Spot-check
   3 employees for correct department, designation, default shift,
   and gender.
4. **Shift + Holiday setup.** Open Holiday List — confirm the list
   has all dates and weekly-offs from `holidays.csv`. Open Shift Type
   — confirm `last_sync_of_checkin` is populated (LEARNINGS #42: this
   is required for auto-attendance to work).
5. **Leave policy + leave allocation.** Apply a single leave
   allocation for one employee using one of the leave types. Confirm
   the per-leave-type defaults from `tenant_config.json` flowed
   through (e.g. max_leaves_allowed, is_carry_forward).
