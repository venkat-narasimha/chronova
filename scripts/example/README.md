# migrate_tenant_data.example — Working Example

This directory is a **complete, runnable example** of the input data
that `migrate_tenant_data.py` expects. It's wired up for a fictional
200-bed medical college & teaching hospital ("Greenwood Medical College
& Hospital" / GMCH) with 20 sample employees.

You can use this directory in two ways:

1. **As a reference** — when onboarding a new client, copy this folder
   to `data/<client-slug>/`, edit the values, then run the migration.
2. **As a smoke test** — point the script at this directory to verify
   the code works end-to-end on a clean site.

## File Index

| File | DocType | Required | Schema |
|------|---------|:--------:|--------|
| [`tenant_config.json`](#tenant_configjson) | (config) | ✅ | JSON object — see below |
| [`company.csv`](#companycsv) | Company | ✅ | one row |
| [`department.csv`](#departmentcsv) | Department | ✅ | one row per department |
| [`designation.csv`](#designationcsv) | Designation | ✅ | one row per job title |
| [`employee.csv`](#employeecsv) | Employee | ✅ | one row per staff member |
| [`shift_type.csv`](#shift_typecsv) | Shift Type | ✅ | one row per shift |
| [`holiday_list.csv`](#holiday_listcsv) | Holiday List | ✅ | one row per list (typically 1) |
| [`holidays.csv`](#holidayscsv) | Holiday (child) | ✅ | one row per holiday, joined to list |
| [`leave_type.csv`](#leave_typecsv) | Leave Type | ✅ | one row per leave type |
| [`leave_policy.csv`](#leave_policycsv) | Leave Policy | ✅ | one row per policy |
| [`leave_policy_detail.csv`](#leave_policy_detailcsv) | Leave Policy Detail (child) | ✅ | one row per mapping, joined to policy |
| [`shift_assignment.csv`](#shift_assignmentcsv) | Shift Assignment | ✅ | one row per assignment |

**Optional CSVs** (only migrate if the file exists in your data dir):

| File | DocType | Trigger |
|------|---------|---------|
| `gender.csv` | Gender | file present |
| `employment_type.csv` | Employment Type | file present |
| `shift_location.csv` | Shift Location | file present (required if `shift_assignment.csv` references a `shift_location`) |
| `shift_request.csv` | Shift Request | file present (rarely used; subject to autoname gotcha) |
| `name_remap.csv` | (cross-env remap) | file present (old_name,new_name) |

---

## tenant_config.json

Tenant-level metadata that doesn't fit in any single DocType row.

| Field | Type | Required | Example | Notes |
|-------|------|:--------:|---------|-------|
| `company_name` | string | ✅ | `"Greenwood Medical College & Hospital"` | Must match `name` in `company.csv` |
| `company_abbr` | string | ✅ | `"GMCH"` | ≤5 chars, used in autoname series (e.g. `HR-SHA-2026-11-00001`) |
| `country` | string | | `"India"` | defaults to India |
| `default_currency` | string | | `"INR"` | ISO 4217 code |
| `fiscal_year_start_month` | int (1-12) | | `4` | April for India |
| `timezone` | string | | `"Asia/Kolkata"` | IANA tz |
| `shift_naming_convention` | string | | `"prompt"` | `"prompt"` or `"field:<fieldname>"` |
| `department_root` | string | | `"All Departments"` | Skip parent_department == this |
| `item_group_root` | string | | `"All Item Groups"` | (not used in college scope) |
| `approver_user` | string | | `"Administrator"` | Pre-seeded as Shift Request approver |
| `default_shift_location` | string\|null | | `"Main Campus - Hyderabad"` | Used if `shift_location.csv` absent |
| `holidays_fiscal_year_label` | string | | `"FY 2026-27"` | Cosmetic, used in Holiday List naming |
| `leave_type_defaults` | object | | `{...}` | Per-leave-type defaults (see below) |

### `leave_type_defaults` schema

A map of `leave_type_name` → default field values. These are **merged
into** the `leave_type.csv` row (CSV wins on conflict) so the JSON
carries only true defaults and the CSV carries client-specific values.

```json
{
  "Privilege Leave": {
    "max_leaves_allowed": 24,
    "is_carry_forward": 1,
    "carry_forward_balance": 12,
    "applicable_after": 0,
    "max_continuous_days_allowed": 30
  }
}
```

---

## company.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | Must match `tenant_config.company_name` |
| `abbr` | string | ✅ | ≤5 chars, must match `tenant_config.company_abbr` |
| `country` | string | ✅ | Used by HRMS for statutory rules |
| `default_currency` | string | ✅ | ISO 4217 |
| `fiscal_year_start_month` | int | | 1-12 |
| `timezone` | string | | IANA tz |

**Optional** (any Frappe Company field can go in the CSV — default
account fields are deferred to a 2-step insert per Gotcha #2):

- `default_receivable_account`, `default_payable_account`,
  `default_bank_account`, `default_cost_center`,
  `round_off_account`, `write_off_account`,
  `exchange_gain_loss_account`, etc.

These are applied via `frappe.db.set_value` AFTER the Company row
exists. If the referenced Account / Cost Center doesn't exist yet,
the set_value call will fail — migrate accounting data FIRST if you
need these.

---

## department.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | Unique within company |
| `parent_department` | string | | Use `tenant_config.department_root` (default `All Departments`) for top-level |
| `company` | string | ✅ | Must match `company.name` |
| `is_group` | int (0/1) | | Set to `1` if the dept has child departments |

**Hierarchy rule:** rows are processed in the order they appear in the
CSV. Parents must appear BEFORE children. The script does not do a
topological sort — it relies on CSV order.

Example hierarchy from this folder:

```
All Departments
├── Medical College  (is_group=1)
│   ├── Pre-Clinical
│   ├── Para-Clinical
│   └── Clinical
└── Hospital  (is_group=1)
    ├── Cardiology
    ├── Orthopedics
    ├── Nursing
    └── Administration  (is_group=1)
        └── HR
```

---

## designation.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | Unique (typically the same as `designation_name`) |
| `designation_name` | string | ✅ | Human-readable label |
| `description` | string | | Free-text, shown in employee form |

---

## employee.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | Use the client's HR code (e.g. `HR-EMP-00001`) |
| `first_name` | string | ✅ | |
| `last_name` | string | | |
| `company` | string | ✅ | Must match `company.name` |
| `department` | string | ✅ | Must match `department.name` |
| `designation` | string | ✅ | Must match `designation.name` |
| `date_of_joining` | date | ✅ | `YYYY-MM-DD` |
| `date_of_birth` | date | ✅ | `YYYY-MM-DD` |
| `gender` | string | ✅ | Must match `gender.csv` row, or built-in (`Male`/`Female`/`Other`) |
| `status` | string | | `Active` / `Inactive` / `Suspended` |
| `employment_type` | string | | Must match `employment_type.csv` row (or built-in `Full-time`) |
| `default_shift` | string | ✅ | Must match `shift_type.name` |
| `reports_to` | string | | `name` of another Employee (creates org chart) |

**Order rule:** Employees are processed in CSV order. If employee X's
`reports_to` points to employee Y, Y must appear BEFORE X in the CSV.

---

## shift_type.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | Shift Type's autoname='prompt' — this is the canonical name |
| `start_time` | time | ✅ | `HH:MM:SS` |
| `end_time` | time | ✅ | `HH:MM:SS`; can cross midnight (e.g. `00:00:00`) |
| `holiday_list` | string | | Must match `holiday_list.name` |
| `enable_auto_attendance` | int (0/1) | | |
| `last_sync_of_checkin` | datetime | | **REQUIRED** for auto-attendance to work (see LEARNINGS #42) |
| `working_hours_threshold_for_half_day` | int | | Hours below which attendance is marked Half Day |

---

## holiday_list.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | Holiday List name |
| `from_date` | date | ✅ | First date in the list's range |
| `to_date` | date | ✅ | Last date in the list's range |
| `weekly_off` | string | | Semicolon-separated day names: `Saturday;Sunday` |
| `color` | string | | Hex color for calendar display |
| `company` | string | | Must match `company.name` |

---

## holidays.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `holiday_list` | string | ✅ | Must match `holiday_list.name` |
| `holiday_date` | date | ✅ | `YYYY-MM-DD` |
| `description` | string | ✅ | |
| `weekly_off` | int (0/1) | | Mark as weekly-off (typically 0 for fixed holidays) |

**Note:** holidays are processed as a child table of Holiday List.
Each Holiday List can have unlimited holidays. The script rebuilds
the child rows on every run (idempotent).

---

## leave_type.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | |
| `max_leaves_allowed` | int | ✅ | Annual allocation |
| `applicable_after` | int | | Days of service before eligible |
| `is_carry_forward` | int (0/1) | | |
| `carry_forward_balance` | int | | Max carry-forward days |
| `max_continuous_days_allowed` | int | | |
| `is_pro_rata` | int (0/1) | | Allocate on joining-date-pro-rata |
| `is_lwp` | int (0/1) | | Mark as Leave Without Pay |
| `include_holiday` | int (0/1) | | |
| `is_optional` | int (0/1) | | |
| `color` | string | | Hex color |

**Defaults merge:** values from `tenant_config.leave_type_defaults.<leave_name>`
are applied FIRST, then the CSV row overrides. So `tenant_config` is
for org-wide policy; CSV is for client-specific customisation.

---

## leave_policy.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | Policy name |
| `applicable_for` | string | | `All Employees` / `Employee Grade` / etc. |
| `company` | string | | |
| `leave_policy_details` | int | | Count of detail rows (informational; ignored by script) |

---

## leave_policy_detail.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `leave_policy` | string | ✅ | Must match `leave_policy.name` |
| `leave_type` | string | ✅ | Must match `leave_type.name` |
| `max_leaves_allowed` | int | | Override of the per-type value |
| `annual_allocation` | int | | Override of the per-type value |

---

## shift_assignment.csv

| Column | Type | Required | Notes |
|--------|------|:--------:|-------|
| `name` | string | ✅ | SA's autoname. Pattern: `<PREFIX>-<YY>-<MM>-#####` |
| `employee` | string | ✅ | Must match `employee.name` |
| `shift_type` | string | ✅ | Must match `shift_type.name` |
| `start_date` | date | ✅ | |
| `end_date` | date | | Omit for open-ended assignment |
| `status` | string | ✅ | `Active` / `Inactive` |
| `docstatus` | int (0/1) | | `1` = submitted |
| `company` | string | | |
| `shift_location` | string | | Must match `shift_location.name` (or `tenant_config.default_shift_location`) |

**Gotcha #9:** the `shift_schedule_assignment` link is **always NULL'd**
by the script because the helper DocType is out of scope.

---

## How to run this example

```bash
# Dry run (validate + report only)
python migrate_tenant_data.py \
    --tenant-config scripts/example/tenant_config.json \
    --data-dir      scripts/example/ \
    --site          <your-site-name> \
    --dry-run

# Live run (insert/update)
python migrate_tenant_data.py \
    --tenant-config scripts/example/tenant_config.json \
    --data-dir      scripts/example/ \
    --site          <your-site-name>
```

Expected dry-run output (approx):

```
PROCESSING Company            (1 rows from company.csv)
PROCESSING Department         (10 rows from department.csv)
PROCESSING Designation        (15 rows from designation.csv)
PROCESSING Shift Type         (5 rows from shift_type.csv)
PROCESSING Holiday List       (1 rows from holiday_list.csv)
PROCESSING Employee           (20 rows from employee.csv)
PROCESSING Leave Type         (9 rows from leave_type.csv)
PROCESSING Leave Policy       (1 rows from leave_policy.csv)
PROCESSING Shift Assignment   (20 rows from shift_assignment.csv)

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

---

## How to adapt for a new client

1. Copy this directory to `data/<client-slug>/` (e.g. `data/stmarys-medical/`).
2. Edit `tenant_config.json` for the client (company name, currency, FY start, etc.).
3. Edit each CSV. Replace example names with the client's data.
4. Optionally add `shift_location.csv` if the client has multiple locations.
5. Run dry-run; review the report.
6. Run live; verify in the Frappe HR UI.

For a college (no clinical staff), the main edits are:
- Department list: drop Clinical/Para-Clinical branches; add Arts/Science/Commerce/Exam Branch.
- Designation list: drop Medical Officer / Senior Resident / Nursing roles; add Lecturer / Tutor / Lab Assistant / Librarian / Registrar.
- Holiday list: swap India-specific holidays for state-specific or country-specific dates.
- Leave type naming: PL/CL/SL stays the same; Medical/Maternity leave may rename.

See `../docs/HOW-TO-ADD-A-NEW-CLIENT.md` for the full step-by-step
onboarding guide.
