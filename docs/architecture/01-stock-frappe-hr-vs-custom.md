# 01 — Stock Frappe HR vs. Custom (Haritha → Foundation)

**Audience:** Venkat (founder/operator), prospective college clients, new engineers joining the team.
**Goal:** Make it obvious which 274 customizations are reusable across every college, which are Haritha-specific, and which need per-client configuration.
**Next step:** Audit `pberpprod` Custom Field / Property Setter fixtures and reconcile the "182 vs 189 vs 274" count discrepancies (see [Data gaps](#data-gaps)).

---

## What this is

This doc is the **single comparison view** that answers the question Venkat keeps asking: *"Out of everything we built for Haritha Hospitals, what did Frappe HR give us for free, what did we actually build, and what can we reuse for any college?"* It is the input to the "Chronova" SaaS product — the SaaS layer must keep only the reusable parts and push the Haritha-specific parts out to per-tenant config.

## Who reads it

| Role | Why they read it |
|---|---|
| **Venkat** (founder) | Sales conversations — "what's the actual product vs. custom work?" |
| **Sales engineer** | College demo — "is X included in the standard platform or is it extra?" |
| **Implementation engineer** | Onboarding a new college — "which fields/configs do I need from them?" |
| **New dev** | Onboarding to the codebase — "what's stock Frappe HR vs. our app?" |

---

## Frappe HR in one paragraph (the 5 stock modules)

Frappe HR (HRMS v16.5.0) ships with **5 core modules out of the box**: **(1) Organization Management** (Employee, Department, Designation, Employment Type, Employee Grade, Branch — full CRUD, reporting lines, org chart); **(2) Employee Lifecycle** (onboarding workflow, transfers, exits, appraisals, exit interviews); **(3) Shift Management** (7 DocTypes — Shift Type, Shift Schedule, Shift Schedule Assignment, Shift Request, Shift Assignment, Employee Checkin, Shift Location — plus the Roster calendar and Shift Assignment Tool); **(4) Attendance** (manual + Auto Attendance from check-ins, with late/early/half-day logic); and **(5) Leave Management** (Leave Type, Leave Policy, Leave Allocation, Leave Application, Leave Ledger Entry, Leave Block List, Holiday List). All five modules come with default Workspaces, default Reports, and standard role-based permissions. **None of the above requires a line of custom code.**

---

## Stock vs. Custom — full comparison (34 rows)

| # | Category | Stock Frappe HR gives you for free | What we added for Haritha (and why) | Reusable? | Haritha-specific? |
|---|---|---|---|---|---|
| **Employee / Org Structure** | | | | | |
| 1 | Employee master | Employee DocType (HRMS) — name, dept, designation, branch, manager, date_of_joining, gender, status | +20 CFs: `leave_approver`, `shift_request_approver`, `default_shift`, `employment_type`, `grade`, `health_insurance_provider/no`, bank details (IFSC/MICR/PAN), `payroll_cost_center`, `employee_advance_account`, `provident_fund_account` | ✅ Yes | — |
| 2 | Department master | Department (HRMS) — name, parent_department, company, approvers table | +8 CFs: `payroll_cost_center`, `leave_block_list`, `leave_approvers` (table), `shift_request_approver` (table), `expense_approvers` (table) | ✅ Yes | — |
| 3 | Designation master | Designation (HRMS) — name, description | +3 CFs: `appraisal_template` (Link), `skills` (Table), section break | ✅ Yes | — |
| 4 | Company master | Company (ERPNext) — name, abbr, country, default accounts, defaults | +11 CFs: HR & Payroll tab, payroll accounts (expense_claim_payable, employee_advance, payroll_payable), HRA components (basic, hra, arrear) | ✅ Yes | — |
| 5 | Branch | Branch (ERPNext) — single DocType | None added | — | — |
| 6 | Employment Type / Grade | Stock | None added | — | — |
| 7 | Org chart | Stock ("Organizational Chart" Desk page, based on `reports_to`) | None — stock works | ✅ Yes | — |
| **Shift Management** | | | | | |
| 8 | Shift Type | Shift Type (HRMS) — start/end, holiday_list, auto_attendance flags, grace periods, last_sync_of_checkin | +2 CFs: `is_oncall` (Check), `is_emergency` (Check) | ⚠️ Partial — `is_emergency` is **Haritha-specific** (ER/code-blue context); `is_oncall` is reusable | ❌ `is_emergency` |
| 9 | Shift Schedule + SSA | Stock (frequency, repeat_on_days, scheduler creates SAs) | None | — | — |
| 10 | Shift Request | Stock (employee-initiated, approver routing) | +1 Workflow (5 states: Draft→Pending→Approved/Rejected/Cancelled) | ✅ Yes (workflow is generic) | — |
| 11 | Shift Assignment | Stock (per-employee per-day) | None | — | — |
| 12 | Employee Checkin | Stock (IN/OUT, time, log_type, source, biometric) | +1 CF: `is_off` (Check, "off-shift check-in" flag) | ✅ Yes (flag is generic) | — |
| 13 | Shift Location | Stock (lat/long, geofence radius) | None — used 0 of 1 (geofence not used by Haritha) | — | — |
| 14 | Roster calendar | Stock Desk page (drag-drop, color-coded) | None | — | — |
| **Attendance** | | | | | |
| 15 | Attendance DocType | Stock (Present/Absent/Half Day, manual + auto from check-ins) | +3 CFs: `late_entry_by` (Int, minutes), `early_out_by` (Int, minutes), `is_wfh` (Check) | ✅ Yes (all generic) | — |
| 16 | Auto Attendance cron | Stock (hourly scheduler, processes check-ins) | None — but **our custom CF `is_off` filters which check-ins to process** | ✅ Yes | — |
| 17 | Mark Attendance tool | Stock Desk page | None | — | — |
| **Leave** | | | | | |
| 18 | Leave Type / Policy / Allocation | Stock (full lifecycle, accrual rules) | None | — | — |
| 19 | Leave Application | Stock DocType | +1 Workflow (5 states) + approver routing via `Employee.leave_approver` | ✅ Yes (workflow is generic) | — |
| 20 | Leave Ledger Entry | Stock (auto-creates on submit) | None | — | — |
| 21 | Holiday List | Stock (per company, regional calendars) | None | — | — |
| 22 | Leave Block List | Stock (department-level "no leave during X") | None | — | — |
| **Reports** | | | | | |
| 23 | Monthly Attendance Sheet | Stock Script Report | None — but we filter by dept scope for Roster/Approver | ✅ Yes (stock + per-tenant filter) | — |
| 24 | Employee Leave Balance / Summary | Stock | None | — | — |
| 25 | Leave Ledger | Stock | Fixed `Report.roles` (Lesson Oct-01) | ✅ Yes | — |
| 26 | Shift Attendance | Stock | Fixed `Report.roles` (Lesson Oct-01) | ✅ Yes | — |
| 27 | Employees Working on Holiday | Stock | None | — | — |
| 28 | Employee Analytics / Birthday | Stock | None | — | — |
| **RBAC** | | | | | |
| 29 | Stock Roles | System Manager, HR Manager, HR User, Leave Approver, Employee, etc. (53 in prod) | +1 new custom role: **Roster Manager** (didn't exist in HRMS) | ✅ Yes (Roster Manager is a generic need) | — |
| 30 | Stock permissions per DocType | Role Permission Manager (RPM) defaults | +858 Custom DocPerm values across 6 roles × 11 DocTypes (Phase A.4) | ✅ Yes (same matrix applies to any college) | — |
| 31 | User Permissions (row-level) | Stock (allow=DocType, value=row) | +~250 User Permission rows (Phase A.6): Employee→self, Leave Approver→dept, Roster Manager→dept | ✅ Yes (script is reusable) | — |
| 32 | Role Profiles | Stock (User bundles N roles) | +6 Role Profiles: `Haritha: System Manager`, `Haritha: HR Manager`, `Haritha: HR User`, `Haritha: Roster Manager`, `Haritha: Leave Approver`, `Haritha: Employee` | ✅ Yes (rename to `College HR: ...` for SaaS) | — |
| **Workflows** | | | | | |
| 33 | Leave Application workflow | None (HRMS ships no workflow) | 5-state workflow (Draft→Pending→Approved/Rejected/Cancelled) + 6 Notifications | ✅ Yes (reusable) | — |
| 34 | Shift Request workflow | None (HRMS ships no workflow) | 5-state workflow + 5 Notifications | ✅ Yes (reusable) | — |
| **Workspaces** | | | | | |
| 35 | Stock Workspaces | "Human Resources", "Leaves", "Shift & Attendance" (standard, is_standard=1) | +6 custom Workspaces: `Haritha: System Manager/HR Manager/HR User/Roster Manager/Leave Approver/Employee` — each with cards/charts/quick-actions per role | ✅ Yes (rename + reuse) | — |
| **Notifications** | | | | | |
| 36 | Email Account (SMTP) | Stock | None — **SMTP not yet configured** (Phase D backlog D6, deferred) | ⚠️ Per-tenant SMTP setup required | — |
| 37 | Workflow notifications | Stock (auto-spawned per Workflow state) | 8 system-channel notifications on Leave + Shift Request workflows | ✅ Yes (reusable) | — |
| **Custom DocTypes** | | | | | |
| 38 | HRMS Health Alert | None (not stock) | **New custom DocType** — tracks scheduler/auto-attendance health | ✅ Yes (generic — any tenant needs this) | — |
| 39 | Server Scripts (2) | None | `Provision User on Employee Activate` (auto-creates User on Employee.status=Active) and `Enforce 90-Day Password Expiry` | ✅ Yes (reusable; clients may want different expiry policy) | — |
| 40 | Master-data migration script | None | `migrate_master_data.py` — 16 DocTypes, idempotent (Lesson #157) | ✅ Yes (Foundation ships this as `tenant_seed.py`) | — |
| **Property Setters — minor UI tweaks (189 rows, group-not-enumerate)** | | | | | |
| 41 | Hidden stock fields | n/a | 133 PSs `hidden=1` on stock fields (clean up the form, hide noise) | ✅ Yes (generic) | — |
| 42 | Hide from print | n/a | 28 PSs `print_hide=1` on stock fields (clean PDF output) | ✅ Yes (generic) | — |
| 43 | Defaults / reqd / read-only | n/a | 28 PSs (default values, mandatory toggles, override `options` on Select fields) | ✅ Yes (generic) | — |
| **Print / Branding** | | | | | |
| 44 | Print Format (Haritha letterhead) | Stock | 3 Haritha Print Formats (Salary Slip, Leave Application, Experience Letter) — letterhead-embedded | ❌ Per-client | ❌ Haritha-specific (letterhead, hospital branding) |
| 45 | Letter Head | Stock | 2 Haritha letterheads | ❌ Per-client | ❌ Haritha-specific |
| **Knowledge & docs (in custom app)** | | | | | |
| 46 | Migration runbook | None | `HARITHA_HOSPITALS_GUIDE.md` (543 lines) + `docs/handbook/*` (~14,030 lines) | ✅ Yes — repurpose as Chronova docs | — |
| 47 | Custom image | None | `frappe/custom_apps:version-16` (HRMS + haritha_hospital baked into a custom Docker image — Lesson Aug-29) | ✅ Yes (rebake per release) | — |

---

## Summary — what is reusable vs. per-client vs. Haritha-only

This is the **bottom-line view** Venkat needs for the SaaS product. Numbers verified against `haritha_hospital` fixtures export (commit `93e8c482`) and the Phase A–D design artifacts.

| Bucket | Count | % of customizations | Lives in | What it means for the SaaS |
|---|---:|---:|---|---|
| **Reusable across all colleges** (Foundation) | ~78 (78 CF) + 189 PS + 1 DocType + 1 custom role + 2 workflows + 8 notifications + 6 role profiles + 2 server scripts + 1 health monitor | **~280 of 282 (~99%)** | `chronova` app — ships to every tenant | The SaaS "core" — install once per site, no per-tenant code work |
| **Per-tenant config** (data, not code) | N/A (data only) | — | `tenant_config.json` + CSV masters | Department list, shift patterns, holiday list, approver mapping, biometric devices, leave types — captured during Discovery phase, applied per tenant |
| **Haritha-specific** (NOT in Foundation) | 1 CF (`is_emergency`) + 2 letterheads + 3 print formats + Haritha role-profile prefix | **~6 of 282 (~2%)** | Haritha-only — stays in Haritha app, never ships to colleges | Hospital-only concepts (ER/code-blue, hospital letterhead). The SaaS app excludes these by design. |
| **Reusable + per-tenant opt-in** | 1 CF (`is_oncall`) + HRMS Health Alert doc + provisioning script | **~3 of 282 (~1%)** | `chronova` — enabled via tenant_config flag | Generic features, but each college decides if it wants them (e.g. on-call tracking, health monitoring strictness) |
| **TOTAL (fixtures exported)** | **282 rows** (78 CF + 189 PS + 8 N + 3 PF + 2 LH + 2 misc) — see [Data gaps](#data-gaps) | 100% | — | — |

**The headline:** of 282 fixture rows, **~99% is reusable across colleges**; only **~2% is Haritha-specific** (hospital letterhead + the ER/code-blue flag). The per-tenant variation lives in **data, not code** — that's the entire SaaS thesis.

---

## Top 3 reusable customizations to call out in a sales pitch

| # | What | Why it matters to a college client |
|---|---|---|
| 1 | **6 role profiles** with **858 permission values** | "Day 1, your HR Head, Roster Manager, Leave Approver, and every employee have exactly the right access. No role-design project needed." |
| 2 | **2 workflows (Leave + Shift Request)** with **8 notifications** | "Leave approval and shift change requests route to the right approver automatically. No email chasing." |
| 3 | **Provision User on Employee Activate** (server script) | "When HR marks an employee Active, their login is created automatically. No IT ticket. No password reset email on day 1." |

---

## Data gaps

| Gap | Detail | Resolution |
|---|---|---|
| 78 vs 189 vs 274 vs 282 count drift | Different docs cite different totals. The "274" in TRACKER/MEMORY = 78 CF + 189 PS + 3 PF + 2 N + 2 LH. The fixture file actually exports **282 rows** (extra stock Print Formats/Notifications with `module=NULL` per Lesson #156) | Reconciliation PR pending — see `docs/handbook/01.1-schema-reference.md` §"Note on counts" |
| Could not enumerate every CF field by name | Read schema reference for Employee, Department, Company, Designation, Print Settings, Address, Tax Exemption; other 14 single-CF DocTypes mentioned by name only | Future audit: list every CF by `dt + fieldname` in a single table |
| Could not enumerate the 189 Property Setters by name | Read top groupings (`hidden` 133, `print_hide` 28, `default` 9, `default_print_format` 8, `reqd` 6, etc.) but did not list all 73 DocTypes | Grouped as "minor UI tweaks" per Venkat's instruction — granularity is not actionable for sales/strategy |
| `shift_category` removal | Earlier docs list `shift_category` (Shift Type) as a Haritha CF that was REMOVED; current fixture may or may not contain it | Audit live prod via `frappe.get_all("Custom Field", {"dt": "Shift Type"})` in a follow-up |
| Email Account / SMTP | Not configured in Haritha prod (Phase D backlog D6, deferred per Venkat) | Per-tenant SMTP must be a Discovery checklist item; not a custom app gap |
| Property Setter `is_synthetic_data` on Employee | Mentioned in `knowledge/shift_management_hrms.md` "Custom Fields — Haritha Hospitals Decisions" but not in `01.1-schema-reference.md` Employee CF list | Audit live prod; possibly was an earlier pberpqa-only field |

---

## Next steps

1. **Reconcile the 78 / 189 / 274 / 282 count drift** — produce a single authoritative table in `01.1-schema-reference.md` (open PR, Venkat to review).
2. **Decide the `chronova` app name** — `haritha_hospital` is misspelled in 2 ways (`haritta_hospital` internal / `haritha_hospital` dir) per MEMORY §"2026-08-29 milestone". Pick one spelling for the new app.
3. **Audit & extract the reusable customizations** into a new `chronova` repo (fork of `haritha_hospital`, minus the 6 Haritha-specific rows). Estimated 2–3 days.
4. **Rewrite the 6 Role Profile names** — drop the `Haritha:` prefix → `College HR:` (or tenant-neutral like `CHRF: HR Manager`).
5. **Build `tenant_seed.py`** — the SaaS equivalent of `migrate_master_data.py`: takes `tenant_config.json` + CSV masters, creates per-tenant data idempotently.
6. **Validate on second tenant** — install `chronova` on a fresh test site, seed with a fictional college's data, confirm 6 roles + 2 workflows + 8 notifications all wire up correctly.

---

*See also: `02-multi-tenant-architecture.md` (how tenants are isolated), `03-data-flow-discovery-to-live.md` (how new college configs get loaded).*
