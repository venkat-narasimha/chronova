# HOW-TO: Add a New Client to the Tenant Migration Pipeline

A step-by-step playbook for onboarding a new college (or any HR) client
to a Frappe HR site using `migrate_tenant_data.py`. Replaces ad-hoc
custom scripts with a config-driven, idempotent, re-runnable flow.

---

## Prerequisites

| Prereq | Verify with |
|--------|-------------|
| Target Frappe HR site is up and accessible | `curl -I https://<site-url>/api/method/ping` returns 200 |
| HRMS app installed on site | `bench --site <site> execute frappe.get_installed_apps` includes `hrms` |
| `migrate_tenant_data.py` lives in a custom app's `utils/` dir | `ls <bench>/apps/<your_app>/<your_app>/utils/migrate_tenant_data.py` |
| Client has filled **Template A1** (Employee master), **A6** (Shift/Leave policy), **A7** (Holiday calendar) | ask client / check `data/<client>/forms/` |

---

## Step 1 — Receive Filled Templates from the Client

The client fills three intake templates (Excel/Google Sheets):

| Template | Content | Required rows |
|----------|---------|---------------|
| **A1** — Employee master | name, DOB, DOJ, dept, designation, gender, default shift, reports_to | 1+ per employee |
| **A6** — Shift + Leave policy | shift types (start/end/break), leave types (max days, carry-forward), leave policy (which types apply) | 1+ shift, 1+ leave type, 1+ policy |
| **A7** — Holiday calendar | holiday list name, fiscal year range, list of dates + descriptions | 1+ holiday list, 1+ holiday |

**Expected output of this step:** three Excel files in
`data/<client-slug>/forms/`.

**Verify with the client:**
- [ ] All Employee names follow the client's ID convention (`HR-EMP-#####`, `CLG-FAC-#####`, etc.).
- [ ] Every `reports_to` value in A1 references another `name` in A1 (or is blank).
- [ ] Every `department` / `designation` / `default_shift` in A1 has a matching row in A1's own "lookups" tab, OR the migration will create them as part of the same payload.

---

## Step 2 — Create the Client Data Folder

```bash
mkdir -p data/<client-slug>/
# Example: data/stmarys-medical/
```

The folder name (`<client-slug>`) should be:
- Lowercase, no spaces, dash-separated
- Identical to the site folder name where possible (e.g. `stmarys.duckdns.org` → `stmarys`)

**Verify:** `ls -la data/<client-slug>/` shows an empty (or `forms/`-only) directory.

---

## Step 3 — Author the tenant_config.json

Copy the example and edit for the client:

```bash
cp scripts/example/tenant_config.json data/<client-slug>/tenant_config.json
```

**Edit these fields:**

| Field | Example | Notes |
|-------|---------|-------|
| `company_name` | `"St. Mary's Medical College & Hospital"` | Must match `company.csv` `name` |
| `company_abbr` | `"SMCH"` | ≤5 chars, used in autoname series |
| `country` | `"India"` | |
| `default_currency` | `"INR"` | |
| `fiscal_year_start_month` | `4` | 4 = April (India FY) |
| `timezone` | `"Asia/Kolkata"` | |
| `default_shift_location` | `"Main Campus - Mumbai"` | The single location used by most clients; or `null` if multiple |
| `approver_user` | `"Administrator"` | Pre-seeded as Shift Request approver |
| `leave_type_defaults` | (see below) | Defaults merged into leave_type.csv per row |

**Verify:** `python3 -c "import json; print(json.load(open('data/<client>/tenant_config.json'))['company_name'])"` returns the client name.

---

## Step 4 — Convert Filled Templates to CSVs

For each of A1, A6, A7, run the export (Google Sheets → CSV, or Excel
→ CSV UTF-8). Save into the client folder with the canonical filenames
that the script expects:

| Source template | Output CSV(s) | Schema |
|-----------------|---------------|--------|
| A1 — Employee master | `employee.csv` (and optionally `department.csv`, `designation.csv`, `gender.csv`, `employment_type.csv`) | see `scripts/example/README.md` |
| A6 — Shift/Leave | `shift_type.csv`, `leave_type.csv`, `leave_policy.csv`, `leave_policy_detail.csv` | same |
| A7 — Holiday calendar | `holiday_list.csv`, `holidays.csv` | same |

**One-Time Setup tip:** keep the conversion script (`forms_to_csv.py`)
versioned in `data/_tools/` so you can re-run it if the client updates
their templates.

**Verify:** `ls data/<client-slug>/*.csv | wc -l` should be ≥8 (you'll
always have company + department + designation + employee + shift_type
+ holiday_list + holidays + leave_type + leave_policy). With
`leave_policy_detail` it's ≥9.

**Common column-name gotchas to fix in the conversion:**
- "Date of Joining" → `date_of_joining`
- "Employee ID" → `name`
- "Designation" → `designation` (the column header)
- Strip trailing whitespace in headers
- Replace smart quotes (',") with ASCII (',")
- Convert DOB/DOJ from `DD/MM/YYYY` to `YYYY-MM-DD`

---

## Step 5 — Dry-Run

This validates CSV structure, reports what WOULD be inserted/updated,
and exits without modifying any Frappe data.

```bash
# Inside the bench container:
python migrate_tenant_data.py \
    --tenant-config data/<client-slug>/tenant_config.json \
    --data-dir      data/<client-slug>/ \
    --site          <client-site-folder> \
    --dry-run
```

**Expected output (last 15 lines):**

```
=== SUMMARY ===
Company              ins=1    upd=0    fail=0 skip=0
Department           ins=10   upd=0    fail=0 skip=0
Designation          ins=15   upd=0    fail=0 skip=0
Shift Type           ins=5    upd=0    fail=0 skip=0
Holiday List         ins=1    upd=0    fail=0 skip=0
Employee             ins=20   upd=0    fail=0 skip=0
Leave Type           ins=9    upd=0    fail=0 skip=0
Leave Policy         ins=1    upd=0    fail=0 skip=0
Shift Assignment     ins=20   upd=0    fail=0 skip=0
TOTAL: ins=82 upd=0 fail=0 skip=0 (dry_run=True)
```

> On a fresh site, all counts should be `ins=N upd=0 fail=0 skip=0`.

**If you see `fail > 0`:** see the Troubleshooting section below.

---

## Step 6 — Review the Dry-Run Report and Fix Errors

Read the script's stderr/stdout for `FAIL <Doctype>/<name>: <error>`
lines. The first 5 errors per DocType are shown; for the rest, look at
the specific line and Frappe's full error.

**Common dry-run issues:**

| Symptom | Cause | Fix |
|---------|-------|-----|
| `LINK_VALIDATION_ERROR: <field>` | A Link column references a DocType that hasn't been migrated yet | Check the script's `MIGRATION_ORDER`; ensure parent DocType CSV is present |
| `MANDATORY_VALUE_MISSING: gender` | Employee row missing `gender` column | Add `gender` to employee.csv (or include `gender.csv`) |
| `PARENT_NOT_FOUND: All Departments` | department.csv has a row whose `parent_department` was misspelled | Fix the spelling; root should be `tenant_config.department_root` |
| `ValidationError: ... does not have a valid 'doctype'` | CSV row has a column named `doctype` (reserved) | Rename the column |
| Column not found errors | Header typo or extra spaces | `head -1 employee.csv` and compare to `scripts/example/README.md` |

Re-run dry-run after each fix. Once `fail=0` for every DocType, proceed.

---

## Step 7 — Run Live

Same command without `--dry-run`:

```bash
python migrate_tenant_data.py \
    --tenant-config data/<client-slug>/tenant_config.json \
    --data-dir      data/<client-slug>/ \
    --site          <client-site-folder>
```

**Expected output (last 15 lines):**

```
=== SUMMARY ===
Company              ins=1    upd=0    fail=0 skip=0
Department           ins=10   upd=0    fail=0 skip=0
...
TOTAL: ins=82 upd=0 fail=0 skip=0 (dry_run=False)
```

The script commits per DocType, so a partial failure leaves the DB in
a consistent state. Re-running the same command is safe (idempotent):
already-inserted records are updated, not duplicated.

---

## Step 8 — Verify in Frappe HR UI

Log into the site as Administrator, then check each DocType:

| Check | URL path | What to look for |
|-------|----------|------------------|
| Company | `/app/company` | Row exists with correct name, abbr, country, currency |
| Departments | `/app/department` | Tree view shows full hierarchy |
| Designations | `/app/designation` | All 15 rows present |
| Employees | `/app/employee` | All 20 rows; `reports_to` resolves correctly (org chart icon) |
| Shift Types | `/app/shift-type` | All 5 rows; `last_sync_of_checkin` populated |
| Holiday List | `/app/holiday-list` | List exists; 10 holidays in child table |
| Leave Types | `/app/leave-type` | All 9 rows |
| Leave Policy | `/app/leave-policy` | Policy exists; 9 leave_policy_details |
| Shift Assignments | `/app/shift-assignment` | All 20 rows; status=Active, docstatus=1 |

**Functional test (1 week of attendance):**

1. Pick 3 employees (1 Morning, 1 Evening, 1 Night).
2. Create 5 check-ins per employee spread across 5 working days via `/app/employee-checkin`.
3. Run `bench --site <site> execute hrms.hr.doctype.employee_checkin.employee_checkin.mark_auto_attendance`.
4. Verify `/app/attendance` shows the expected Present / Half Day / Absent rows.
5. Verify `/hr/roster/` shows colored cells for the test week.

**Done.** Mark the site "ready" only after steps 1-5 pass.

---

## Troubleshooting — The 10 Gotchas

These are the same 10 from `LEARNINGS.md` Lesson #157, mapped to the
tenant-agnostic version. If your migration fails, find the matching
symptom below.

### Gotcha #1 — "doc(dict) does not have a valid 'doctype'"

**Symptom:** Every insert fails with:
```
ValidationError: doc(dict) does not have a valid 'doctype'
```

**Cause:** A CSV row has a column literally named `doctype`, which
overrides the script's auto-injection of `{"doctype": <doctype>}`.

**Fix:**
1. Find the offending column: `head -1 *.csv | grep -in doctype`
2. Rename it (e.g. `doc_type` or `record_type`).
3. Re-run dry-run.

---

### Gotcha #2 — Company 2-step insert

**Symptom:** `LINK_VALIDATION_ERROR` on `default_receivable_account`
(or any other default-account field) when Company row is inserted.

**Cause:** Account records are not migrated yet. Default-account Links
fail validation at insert time.

**Fix:** The script already handles this — it inserts Company with
identity fields only, then attaches defaults via `set_value`. If you
see this error, it means:
- A) You're running a custom version of the script that bypasses the 2-step path, OR
- B) The CSV's `default_*_account` value references a name that doesn't exist in the target DB at all (typo in account name).

**Action:** verify the account name exists on the target site:
```bash
bench --site <site> execute "frappe.db.exists('Account', '<name>')"
```

---

### Gotcha #3 — Account root nodes (out of scope)

**Symptom:** `DuplicateEntryError` or `parent_account not found` when
inserting Accounting data.

**Cause:** `Accounts Receivable`, `Accounts Payable`, `Cash In Hand`
etc. are system-managed root nodes — never re-create.

**Fix:** Out of scope for the Chronova. If you need to
extend with accounting migration:
```python
# In your custom _migrate_account function:
if record.get("parent_account") in (None, "") and record.get("root_type"):
    continue    # skip system-managed root
```

---

### Gotcha #4 — `Shift Type` autoname='prompt'

**Symptom:** `ValidationError: Please set the document name` on Shift
Type insert.

**Cause:** Shift Type's controller declares `autoname='prompt'`, so
Frappe does NOT auto-generate a name. The CSV must include a `name`
column AND the script must pin it on insert.

**Fix:**
1. Verify `shift_type.csv` has a `name` column (not just `shift_type` or `label`).
2. Verify the script's `upsert()` is being called with the right `name` arg.

The provided `upsert()` handles this — if you see the error, check
that `shift_type.csv` exists and has the right header.

---

### Gotcha #5 — Department / Item Group circular root

**Symptom:** `ParentNotFoundError: All Departments` when inserting a
top-level department.

**Cause:** The script's `department_root` config (default
`All Departments`) doesn't exist on the target site, OR a row in
`department.csv` has `parent_department=All Departments` and the script
isn't skipping it.

**Fix:**
- `All Departments` is created automatically by Frappe on HRMS install.
  If missing, run `bench --site <site> execute hrms.hr.doctype.department.department.create_default_department_tree`.
- If the client uses a different root name, set `department_root` in
  `tenant_config.json` to match.

---

### Gotcha #6 — Employee missing Gender / Default Shift

**Symptom:** `LinkValidationError: gender` or `LinkValidationError: default_shift`
when inserting an Employee.

**Cause:** Either:
- (a) `gender.csv` / `shift_type.csv` is not in the data dir, OR
- (b) The referenced Gender / Shift Type record doesn't exist on the
  target site.

**Fix:**
1. If using built-in Genders (`Male`/`Female`/`Other`), no CSV needed.
2. If using custom Genders, ensure `gender.csv` is in the data dir and
   the script is migrating it.
3. Verify `shift_type.csv` is present and was processed BEFORE
   `employee.csv` (the script's `MIGRATION_ORDER` enforces this).

---

### Gotcha #7 — Employee ID remap (cross-env migration)

**Symptom:** `LinkValidationError: reports_to` or
`LinkValidationError: leave_approver` for some employees.

**Cause:** The CSV's `reports_to` value references an Employee ID that
doesn't exist on the target site. Common when seeding a new site from
a JSON export of an existing site — the source IDs differ from target IDs.

**Fix:** Add `name_remap.csv` to the data dir:
```csv
old_name,new_name
HR-EMP-00211,HR-EMP-00001
HR-EMP-00212,HR-EMP-00002
...
```
The script rewrites every Employee Link field (including `reports_to`)
from `old_name` → `new_name` before insert.

**Alternative (cleaner for new sites):** use the target site's ID
convention in the CSV. The script uses the CSV's `name` column as the
canonical target name — no remap needed.

---

### Gotcha #8 — Child tables stripped (Holiday / Leave Policy details)

**Symptom:** Holiday List or Leave Policy is inserted, but its child
rows are empty.

**Cause:** The Frappe ORM filters child-table rows by parent docstatus
on insert. The script already handles this by appending child rows
programmatically via `doc.append()` AFTER the parent is constructed.
If you see empty children, the script is being bypassed (e.g. you're
inserting via a different code path).

**Fix:** Always use `_migrate_holiday_list` / `_migrate_leave_policy`
helpers. They rebuild children on every run from the side CSV.

---

### Gotcha #9 — Shift Assignment references Shift Location

**Symptom:** `LinkValidationError: shift_location` on Shift Assignment
insert.

**Cause:** `shift_assignment.csv` references a `shift_location` value
that doesn't exist on the target site.

**Fix:**
1. Add `shift_location.csv` to the data dir with the location name(s).
2. OR set `default_shift_location` in `tenant_config.json` and update
   `shift_assignment.csv` to use that name.
3. The script's `MIGRATION_ORDER` migrates Shift Location (if CSV
   present) BEFORE Shift Assignment.

**Note:** `shift_schedule_assignment` is always NULL'd by the script
(it's a helper DocType out of scope for the Chronova).

---

### Gotcha #10 — Shift Request validate_approver + autoname series

**Symptom:**
- (a) `Only Approvers can Approve this Request.` on Shift Request insert
- (b) The inserted `name` doesn't match the CSV's `name` (Frappe renumbered it)

**Cause:**
- (a) The Employee's `approver` is not in the target department's
  `shift_request_approver` list. The script pre-seeds a
  `Department Approver` row with `approver=Administrator` (or
  `tenant_config.approver_user`) for every department referenced by
  the Shift Request data.
- (b) Frappe's autoname series counter is below the requested number;
  Frappe silently discards the explicit `name` and uses the next series
  number. The script pre-bumps the counter via `_pre_set_shift_request_series`.

**Fix:**
- (a) Verify `approver_user` in `tenant_config.json` is a real User on
  the target site (`bench --site <site> execute "frappe.db.exists('User', '<user>')"`).
- (b) Verify the CSV's `name` matches the `HR-SHR-.YY.-.MM.-.#####`
  pattern. If your client uses a different autoname pattern, edit
  `_pre_set_shift_request_series()` in the script.

**Note:** Most college clients don't use Shift Request (it's a
self-service HRMS feature for hospitals). Only triggered if
`shift_request.csv` is in the data dir.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python migrate_tenant_data.py --help` | Show all CLI flags |
| `python -c "import ast; ast.parse(open('migrate_tenant_data.py').read())"` | Verify script is syntactically valid |
| `head -1 data/<client>/*.csv` | Check CSV headers |
| `wc -l data/<client>/*.csv` | Count rows per CSV |
| `bench --site <site> console` | Open Frappe console to inspect the DB |
| `bench --site <site> execute "frappe.db.get_value('Employee', 'HR-EMP-00001', '*')"` | Spot-check a single record |

---

## File Checklist (for client onboarding)

When onboarding a new client, the data folder should have at minimum:

- [ ] `tenant_config.json` (with `company_name`, `company_abbr`, currency, country)
- [ ] `company.csv` (1 row matching `tenant_config.company_name`)
- [ ] `department.csv` (≥1 row, with parents before children)
- [ ] `designation.csv` (≥1 row)
- [ ] `employee.csv` (≥1 row, with `reports_to` resolvable)
- [ ] `shift_type.csv` (≥1 row, with `last_sync_of_checkin` set)
- [ ] `holiday_list.csv` (≥1 row)
- [ ] `holidays.csv` (≥1 row, joined to a holiday_list)
- [ ] `leave_type.csv` (≥1 row)
- [ ] `leave_policy.csv` (≥1 row)
- [ ] `leave_policy_detail.csv` (≥1 row, joined to a leave_policy)

Optional (if client needs):
- [ ] `shift_location.csv` (if multiple locations OR shift_assignment references one)
- [ ] `gender.csv` (if non-standard Gender values)
- [ ] `employment_type.csv` (if non-standard Employment Type values)
- [ ] `shift_request.csv` (rare — only for HRMS self-service flow)
- [ ] `name_remap.csv` (only for cross-env migration)
