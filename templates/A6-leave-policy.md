# A6 — Leave Policy Intake

**Form Code:** A6
**Form Name:** Leave Policy — Entitlements, Accruals & Carry-Forward
**Date:** 2026-10-15
**Version:** v1.0
**Status:** ✅ Ready for prospect use
**Owner:** Venkat Narasimha (Chronova)
**Time to complete:** 30–45 minutes
**Format:** Google Form OR Excel upload (CSV schema embedded below)
**Companion forms:** A1 (Org Profile), A7 (Approval Matrix)
---

## What This Is

This is the **leave policy intake form** Chronova uses to configure a Frappe HR instance that matches the college's existing leave rules. The form captures the **nine standard leave types** that every Indian college / hospital / university should have, with **nine attributes per leave type** — accrual rate, accrual period, carry-forward limit, maximum consecutive days, encashment rules, medical certificate threshold, applicability, approval level, and notice period.

The form's output drives the **Leave Type DocType** in Frappe HR (one Leave Type per row in the CSV) and the **Leave Policy** + **Leave Policy Assignment** setup that bundles entitlements per employee class. Every field has a default, but the default is **Conservative Indian Private Sector** — most clients override at least 6 of the 9 attributes per leave type.

## Who Fills It

The **HR Lead** owns this form but should consult the **Principal / Director** for academic norms (e.g., exam-period leave, study leave for faculty pursuing PhD) and the **Finance Officer** for encashment rules (because encashment is a payroll cash-out event).

For medical colleges, also consult the **Medical Superintendent** for:
- Clinical resident duty-hour limits (NMC cap = 48 hours/week averaged over 4 weeks)
- Maternity leave for female residents (separate from the Maternity Benefit Act 1961 entitlement)
- Sick leave documentation for clinical staff handling patient care

## When To Use It

This form is filled **after A1 (Org Profile)** is signed, typically during **Phase 2 of the B1 discovery meeting**. The consultant walks through each leave type live, captures the answers, and the HR Lead reviews within 48 hours.

The form is **legally sensitive**. Once a college confirms a leave policy in Frappe HR, that policy becomes the auditable record for PF / ESI / Income Tax scrutiny. The consultant should explicitly call out:
- **Leave encashment** is **taxable** under "Income from Salaries" — must be reported in Form 16.
- **Maternity leave** must comply with the **Maternity Benefit (Amendment) Act 2017** — 26 weeks for the first 2 children, 12 weeks for 3rd+ child, 12 weeks for commissioning/adoptive mothers.
- **Leave Without Pay (LWP)** affects **PF contribution** — if LWP exceeds 60 days in a year, PF may not be deposited for that month.
- **Factories Act 1948 §79** (where applicable) and **Shops & Establishments Act** of the relevant state govern weekly holiday and overtime rules.

---

## 1. Leave Type Catalog (9 types)

The 9 leave types below cover ~95% of Indian college / hospital leave policies. If the prospect has a leave type not on this list, add it as a tenth row in the CSV.

### 1.1 Casual Leave (CL)

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | 1 day per month | 12 days per year for permanent staff |
| 2 | **Accrual period** | Dropdown | Monthly | Monthly / Quarterly / Annual lump-sum |
| 3 | **Carry-forward limit** | Number | 0 days | Most colleges lapse CL on 31st December / 31st March |
| 4 | **Max consecutive days** | Number | 3 days at a stretch | Beyond this, switch to SL / EL |
| 5 | **Encashment on separation** | Yes/No | No | CL is rarely encashed |
| 6 | **Medical certificate threshold** | Days | 2 consecutive days | Some colleges require a certificate from Day 1 |
| 7 | **Applicable to** | Multi-select | All employee categories | Teaching, Non-teaching, Medical, Paramedical, Admin, Support |
| 8 | **Approval level** | Dropdown | L1 — Immediate Manager | For teaching: HOD; for non-teaching: reporting officer |
| 9 | **Notice period** | Number (days) | 1 day prior | For planned CL; emergencies exempted |

**Frappe HR mapping:** `Leave Type = "Casual Leave"`, `max_continuous_days_allowed = 3`, `carry_forward = 0`, `is_carry_forward = 0`, `is_lwp = 0`, `is_earned_leave = 0`, `allow_negative = 0`.

### 1.2 Sick Leave (SL)

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | 1 day per month | 12 days per year |
| 2 | **Accrual period** | Dropdown | Monthly | Some colleges grant 6 days lump-sum in Jan + 6 in July |
| 3 | **Carry-forward limit** | Number | 6 days | Common range: 6-12 days |
| 4 | **Max consecutive days** | Number | 10 days at a stretch | Beyond this, requires Medical Board's recommendation |
| 5 | **Encashment on separation** | Yes/No | No | Rarely encashed; some allow up to 50% |
| 6 | **Medical certificate threshold** | Days | 2 consecutive days | Strict colleges require certificate from Day 1 |
| 7 | **Applicable to** | Multi-select | All employee categories | |
| 8 | **Approval level** | Dropdown | L1 — Immediate Manager; **L2 (HOD) mandatory for >3 consecutive days** | Escalation rule: short SL (≤3 days) = L1 only; longer SL (>3 days) requires L2 sign-off. This is the reconciled rule (see validation finding X-3). |
| 9 | **Notice period** | Number (days) | Same day / morning of | Sick leave is by definition unplanned; no prior notice |

**Frappe HR mapping:** `Leave Type = "Sick Leave"`, `max_continuous_days_allowed = 10`, `carry_forward = 6`, `is_carry_forward = 1`, `medical_leave = 1` (custom flag to allow longer post-medical-certification).

### 1.3 Earned Leave (EL) / Privilege Leave (PL)

> These are the same leave type under different names. Use the name the college uses internally.

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | 1.5 days per month (or 1 day per 20 days worked) | 18 days/year — meets Factories Act 1948 §79B (1 day per 20 days for adults) |
| 2 | **Accrual period** | Dropdown | Monthly | Some colleges use "1 day per 20 days worked" (Factories Act style) |
| 3 | **Carry-forward limit** | Number | 30 days (or 45 days for teaching) | Higher for faculty who can't take leave in exam periods |
| 4 | **Max consecutive days** | Number | 30 days at a stretch | For sabbatical, see Special Leaves below |
| 5 | **Encashment on separation** | Yes/No | Yes (subject to cap of 30 days) | Common: encash up to 30 days at basic salary; treat as "Income from Salaries" |
| 6 | **Medical certificate threshold** | Days | N/A | EL is not medical leave |
| 7 | **Applicable to** | Multi-select | All permanent employees | Excludes contract / visiting staff typically |
| 8 | **Approval level** | Dropdown | L2 — HOD / Department Head | Higher than CL because EL impacts long-term balance |
| 9 | **Notice period** | Number (days) | 7 days prior | For planned EL; sabbatical requires 60 days |

**Frappe HR mapping:** `Leave Type = "Earned Leave"`, `is_earned_leave = 1`, `earned_leave_frequency = "Monthly"`, `max_continuous_days_allowed = 30`, `carry_forward = 30`, `is_carry_forward = 1`, `allow_encashment = 1`, `encashment_threshold_days = 30`, `earning_component = "Basic"`.

### 1.4 Maternity / Paternity Leave (ML)

> **Maternity Benefit (Amendment) Act 2017** makes this mandatory: **26 weeks** for first 2 children, **12 weeks** for 3rd+ child or adoption / commissioning. Paternity leave is **not yet** mandatory in India (Bill 2017 pending), but most colleges offer 7-15 days.
>
> **3rd-child rule (statutory, non-negotiable):** The 26-week entitlement applies only to the first **two** surviving children. For the 3rd child, the entitlement drops to **12 weeks (84 days)**. Because Frappe HR cannot apply the 26-vs-12 split conditionally on parity, **a separate Leave Type row is required** — see `Maternity Leave (3rd+ Child)` in the CSV below §4. The consultant must ask the client to clarify the leave-type assignment per pregnancy; the typical rule is to grant ML based on the **count of previous live births** declared in the medical certificate.

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | Lump-sum 182 days (26 weeks) | Statutory minimum — can be higher (some private colleges offer 6 months + 1 month) |
| 2 | **Accrual period** | Dropdown | Lump-sum on pregnancy confirmation | After submission of medical certificate + 8 months of continuous service |
| 3 | **Carry-forward limit** | Number | 0 days | Lapses if not availed in the eligible window |
| 4 | **Max consecutive days** | Number | 182 days (or 84 for 3rd child) | Statutory; cannot be split into <2 segments |
| 5 | **Encashment on separation** | Yes/No | No | Maternity leave is non-encashable |
| 6 | **Medical certificate threshold** | Days | N/A (entire leave is medical) | Submit hospital certificate and expected delivery date |
| 7 | **Applicable to** | Multi-select | Female employees (Maternity); Male employees (Paternity) | Covers all categories; service tenure ≥ 80 days in last 12 months for ML |
| 8 | **Approval level** | Dropdown | L3 — Principal / HR Head | Sensitive, requires top-level sign-off; HR files Form Maternity Benefit. **Note:** A6's "approval level" = the **final authority** on the leave; A7 §2.1 still routes the application through L1 (manager) and L2 (HOD) for prior concurrence. The L3 designation here is the decision-maker, not the only approver — see A7 §1 for the cross-document definition. |
| 9 | **Notice period** | Number (days) | 8 weeks before expected delivery | As per Maternity Benefit Act §6(3) |

**Frappe HR mapping:** Two Leave Types — `Maternity Leave` and `Paternity Leave`. `is_lwp = 0`, `is_paid = 1` (custom), `allow_negative = 0`, `max_continuous_days_allowed = 182` (Maternity) / `15` (Paternity). Add custom field `is_maternity_benefit_act` to ensure compliance reporting.

### 1.5 Compensatory Off (Comp Off)

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | 1 day per extra day worked | Earned when an employee works on a weekly off / public holiday |
| 2 | **Accrual period** | Dropdown | Per occurrence | Granted on the day worked, valid for 30-90 days |
| 3 | **Carry-forward limit** | Number | 30 days | Strict expiry — drives the "use it or lose it" mindset |
| 4 | **Max consecutive days** | Number | 2 days at a stretch | Rare to grant comp off for more than 2 days in a row |
| 5 | **Encashment on separation** | Yes/No | No | Comp off is work-effort-based, not salary-based; rarely encashed |
| 6 | **Medical certificate threshold** | Days | N/A | Not medical leave |
| 7 | **Applicable to** | Multi-select | All employees who work on off-days | Critical for hospital staff (24×7) and exam-period faculty |
| 8 | **Approval level** | Dropdown | L1 — Reporting Officer → L2 — HOD → L3 — HR | L1 verifies the extra day was actually worked; L2 confirms with biometric/attendance; L3 (HR) releases the comp-off credit to leave balance. **Note:** A6's "approval level" = **final authority**; full chain is L1→L2→L3 — see A7 §2.4. |
| 9 | **Notice period** | Number (days) | 3 days prior (when availing) | Plan the comp-off in advance |

**Frappe HR mapping:** `Leave Type = "Compensatory Off"`, `is_compensatory = 1` (custom flag), `max_continuous_days_allowed = 2`, `carry_forward = 30`, `is_carry_forward = 1`, `is_paid = 1`.

### 1.6 Leave Without Pay (LWP) / Unpaid Leave

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | N/A — granted on request | Does not accrue; consumed when other leave balances are exhausted |
| 2 | **Accrual period** | Dropdown | On application | |
| 3 | **Carry-forward limit** | Number | N/A | LWP doesn't carry forward (it has no balance to carry) |
| 4 | **Max consecutive days** | Number | 90 days at a stretch | Beyond 90 days, contract is at risk; beyond 6 months, may trigger "break in service" for gratuity |
| 5 | **Encashment on separation** | Yes/No | N/A | LWP is unpaid; nothing to encash |
| 6 | **Medical certificate threshold** | Days | N/A | If for medical reasons, the leave should be SL with cert; LWP is for non-medical gaps |
| 7 | **Applicable to** | Multi-select | All categories | But typically: travel, family obligations, prolonged personal matters |
| 8 | **Approval level** | Dropdown | L3 — Principal / HR Head | High-impact on payroll, PF, gratuity; needs principal sign-off. **Note:** A6's "approval level" = **final authority**; A7 §2.1 still chains the application through L1 (manager) and L2 (HOD) for prior concurrence — see A7 §1. |
| 9 | **Notice period** | Number (days) | 7 days prior | As long as the employee can plan |

**Frappe HR mapping:** `Leave Type = "Leave Without Pay"`, `is_lwp = 1`, `is_paid = 0`, `allow_negative = 0`, `max_continuous_days_allowed = 90`. Set HR Settings → `include_holidays_in_total_leave_days = 0` for LWP calculations.

### 1.7 On-Duty (OD) / Official Duty Leave

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | N/A — granted per occurrence | Allocated when employee is on official work outside campus |
| 2 | **Accrual period** | Dropdown | Per occurrence | E.g., conference attendance, FDP, university inspection, exam duty |
| 3 | **Carry-forward limit** | Number | N/A | OD is event-based, no balance to carry |
| 4 | **Max consecutive days** | Number | 14 days at a stretch | For longer, switch to EL or special leave |
| 5 | **Encashment on separation** | Yes/No | No | OD doesn't reduce balance and doesn't encash |
| 6 | **Medical certificate threshold** | Days | N/A | Not medical leave |
| 7 | **Applicable to** | Multi-select | All categories | Primarily teaching (FDPs, conferences, board exams) |
| 8 | **Approval level** | Dropdown | L2 — HOD + L3 — Principal | Principal approves when OD involves external commitment (conference fee, paper) |
| 9 | **Notice period** | Number (days) | 7 days prior with documentation | Conference brochure / invitation letter / exam notification |

**Frappe HR mapping:** Custom doctype `On Duty Application` (not standard Frappe HR) or use Leave Application with `Leave Type = "On Duty"` + custom field `od_event_details`. Recommended: build a separate workflow-driven DocType `On Duty Request` linked to Event / Conference.

### 1.8 Special Leaves (Bereavement, Marriage, Study, Paternity, Adoption)

> These are typically a **single Leave Type** with **sub-categories** defined in a custom field. Indian labour law does not require these, but they are standard in college HR policies.

| # | Attribute | Type | Typical value | Notes |
|---|-----------|------|---------------|-------|
| 1 | **Accrual rate** | Number + period | Lump-sum based on event | E.g., 7 days bereavement, 5 days marriage, 12 months study, 15 days paternity |
| 2 | **Accrual period** | Dropdown | On event | Triggered by event; submitted with proof |
| 3 | **Carry-forward limit** | Number | 0 days | Lapses if not used within 90 days of event |
| 4 | **Max consecutive days** | Number | Varies by sub-category | 7 (bereavement), 5 (marriage), 365 (study sabbatical) |
| 5 | **Encashment on separation** | Yes/No | No | Special leaves are not encashable |
| 6 | **Medical certificate threshold** | Days | N/A (except paternity — birth certificate required) | |
| 7 | **Applicable to** | Multi-select | All categories | Study sabbatical typically for permanent teaching staff only |
| 8 | **Approval level** | Dropdown | L3 — Principal | All special leaves need principal sign-off; study sabbatical needs Chairman. **Note:** A6's "approval level" = **final authority**; A7 §2.1 still routes the application through L1 (manager) and L2 (HOD) for prior concurrence — see A7 §1. |
| 9 | **Notice period** | Number (days) | 7 days prior (for marriage) / 30 days (for study) | Bereavement is same-day |

**Sub-categories** (custom field `special_leave_category`):

| Sub-category | Days granted | Proof required |
|---|:---:|---|
| Bereavement (immediate family) | 7 | Death certificate |
| Bereavement (extended family) | 3 | Death certificate |
| Marriage (self) | 5 | Wedding invitation |
| Adoption | 12 weeks | Adoption order |
| Study leave (PhD / higher study) | Up to 365 | Admission letter + principal recommendation |
| Jury / civic duty | As required | Court summons |
| Sports / cultural representation | As required | Selection letter from association |

**Frappe HR mapping:** `Leave Type = "Special Leave"`, `is_special_leave = 1` (custom), `is_paid = 1`, `allow_negative = 0`, custom field `special_leave_category` (Select with the 7 sub-categories above — **Paternity consolidated to §1.4 as its own Leave Type to avoid double-counting with the statutory ML-Paternity row**). `max_continuous_days_allowed = 365` (study) with `special_leave_max_days_per_subcategory` (custom child table).

### 1.9 Comp Off — Reference (already covered in 1.5)

> Comp Off is covered under 1.5. This entry is intentionally blank to preserve numbering.

---

## 2. Per-Category Applicability Matrix

Beyond per-leave-type rules, capture how each leave type applies to each **employee category** (defined in A1 §2.1). Mark ✅ (full entitlement), ⚪ (reduced or pro-rated), or ❌ (not applicable).

| Leave Type | Teaching FT | Teaching Visiting | Non-teaching Academic | Medical / Clinical | Paramedical | Admin | Housekeeping / Support |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| CL | ✅ (12/yr) | ⚪ (6/yr) | ✅ (12/yr) | ✅ (12/yr) | ✅ (12/yr) | ✅ (12/yr) | ✅ (12/yr) |
| SL | ✅ (12/yr) | ⚪ (6/yr) | ✅ (12/yr) | ✅ (12/yr) | ✅ (12/yr) | ✅ (12/yr) | ✅ (12/yr) |
| EL | ✅ (18/yr, 30 CF) | ❌ | ✅ (18/yr, 30 CF) | ✅ (24/yr, 30 CF for residents) | ✅ (18/yr) | ✅ (18/yr) | ✅ (15/yr) |
| ML — Maternity | ✅ (26 wk) | ❌ | ✅ (26 wk) | ✅ (26 wk) | ✅ (26 wk) | ✅ (26 wk) | ✅ (26 wk) |
| ML — Paternity | ✅ (7 d) | ❌ | ✅ (7 d) | ✅ (7 d) | ✅ (7 d) | ✅ (7 d) | ✅ (7 d) |
| Comp Off | ✅ (per occurrence) | ❌ | ✅ | ✅ (24×7) | ✅ (shift) | ⚪ (rare) | ✅ (per occurrence) |
| LWP | ✅ (up to 90 d) | ⚪ | ✅ | ✅ | ✅ | ✅ | ✅ |
| OD | ✅ (per event) | ✅ | ✅ | ✅ | ✅ | ⚪ | ❌ |
| Special — Bereavement | ✅ (7 d) | ⚪ (3 d) | ✅ (7 d) | ✅ (7 d) | ✅ (7 d) | ✅ (7 d) | ✅ (7 d) |
| Special — Marriage | ✅ (5 d) | ❌ | ✅ (5 d) | ✅ (5 d) | ✅ (5 d) | ✅ (5 d) | ✅ (5 d) |
| Special — Study | ✅ (up to 365 d) | ❌ | ⚪ | ❌ | ❌ | ❌ | ❌ |
| Special — Adoption | ✅ (12 wk) | ❌ | ✅ (12 wk) | ✅ (12 wk) | ✅ (12 wk) | ✅ (12 wk) | ✅ (12 wk) |

---

## 3. Indian Regulatory Anchors (for the consultant's reference)

| Regulation | Applies to | Key leave rule |
|---|---|---|
| **Factories Act 1948, §79** | Manufacturing (rare for colleges) | 1 day earned leave per 20 days worked for adults |
| **Factories Act 1948, §79B** | All establishments (state-specific) | EL accrual rule varies; some states cap carry-forward at 30 days |
| **Shops & Establishments Act** (state-wise) | Service establishments | Weekly holiday, overtime, leave rules; differs per state |
| **Maternity Benefit (Amendment) Act 2017** | All women employees | 26 weeks for first 2 children, 12 weeks for 3rd+ |
| **Payment of Wages Act 1936** | All employees | Leave encashment must be paid before employee's next pay cycle |
| **Payment of Gratuity Act 1972** | Employees with 5+ years service | LWP > 6 months breaks continuous service for gratuity eligibility |
| **Income Tax Act 1961** | All employees | Encashed leave up to ₹25,00,000 in a year is exempt from tax (old regime; **verify with current FY limit before sending to prospect** — Section 10(10AA) was amended by Finance Act 2023; non-Government employees may no longer qualify for the ₹25L ceiling) |
| **NMC (MCI) Regulations** | Medical colleges | Resident duty hours cap at 48 hrs/week averaged over 4 weeks; affects OD/LWP for residents |
| **UGC Regulations on Minimum Qualifications** | Universities / colleges | Faculty study leave entitlement varies; check UGC 2018 regulations |

---

## 4. CSV Schema (for Excel / Google Sheets import)

One row per **Leave Type**. Each row defines the rules for that leave type as a whole; per-category variations in §2 are applied via Frappe HR's Leave Policy Assignment child tables.

```csv
leave_type,leave_type_code,accrual_rate,accrual_period,carry_forward_limit,max_consecutive_days,encashment_allowed,encashment_cap_days,medical_certificate_threshold_days,applicable_to,approval_level,notice_period_days,is_earned_leave,is_lwp,is_compensatory,is_maternity,is_paternity,is_special,frappe_hr_setup_notes
"Casual Leave","CL",1,Monthly,0,3,No,0,2,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L1-Manager,1,No,No,No,No,No,No,"max_continuous_days_allowed=3; carry_forward=0"
"Sick Leave","SL",1,Monthly,6,10,No,0,2,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L1-Manager,0,No,No,No,No,No,No,"max_continuous_days_allowed=10; carry_forward=6; medical_leave=1"
"Earned Leave","EL",1.5,Monthly,30,30,Yes,30,0,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L2-HOD,7,Yes,No,No,No,No,No,"is_earned_leave=1; earned_leave_frequency=Monthly; allow_encashment=1; encashment_threshold_days=30; earning_component=Basic"
"Maternity Leave","ML-Maternity",26,Weeks-lumpsum,0,182,No,0,0,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L3-Principal,56,No,No,No,Yes,No,No,"is_paid=1; is_lwp=0; max_continuous_days_allowed=182; maternity_benefit_act=1; submit-medical-certificate=Yes; child_count_max=2"
"Maternity Leave 3rd+ Child","ML-Maternity-3rd",12,Weeks-lumpsum,0,84,No,0,0,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L3-Principal,56,No,No,No,Yes,No,No,"is_paid=1; is_lwp=0; max_continuous_days_allowed=84; maternity_benefit_act=1; submit-medical-certificate=Yes; child_count_min=3"
"Paternity Leave","ML-Paternity",7,Days-lumpsum,0,7,No,0,0,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L3-Principal,0,No,No,No,No,Yes,No,"is_paid=1; is_lwp=0; max_continuous_days_allowed=7; require-birth-certificate=Yes"
"Compensatory Off","COMP",1,Per-occurrence,30,2,No,0,0,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L2-HOD-plus-HR,3,No,No,Yes,No,No,No,"is_compensatory=1; max_continuous_days_allowed=2; carry_forward=30; expiry_days=90"
"Leave Without Pay","LWP",0,On-application,0,90,No,0,0,"Teaching|NT-Academic|Medical|Paramedical|Admin|Support",L3-Principal,7,No,Yes,No,No,No,No,"is_lwp=1; is_paid=0; max_continuous_days_allowed=90; break-in-service-tracking=Yes"
"On Duty","OD",0,Per-occurrence,0,14,No,0,0,"Teaching|NT-Academic|Medical|Paramedical|Admin",L2-HOD-plus-L3,7,No,No,No,No,No,No,"custom-doctype-on-duty-application; or leave-application with custom flag"
"Special Leave Bereavement","SPL-BR",7,Event-lumpsum,0,7,No,0,0,"All",L3-Principal,0,No,No,No,No,No,Yes,"is_special=1; sub-category=Bereavement-immediate-family"
"Special Leave Marriage","SPL-MR",5,Event-lumpsum,0,5,No,0,0,"All",L3-Principal,7,No,No,No,No,No,Yes,"is_special=1; sub-category=Marriage-self; lifetime-cap=2"
"Special Leave Paternity Extended","SPL-PT",15,Event-lumpsum,0,15,No,0,0,"All",L3-Principal,0,No,No,No,No,No,Yes,"is_special=1; sub-category=Paternity-extended; require-birth-certificate=Yes; expire-days-after-event=180""Special Leave Study","SPL-SD",365,Event-lumpsum,0,365,No,0,0,"Teaching-FT-only",L3-Principal-plus-Chairman,30,No,No,No,No,No,Yes,"is_special=1; sub-category=Study-PhD; service-tenure-min=3-years; bond-period=2-years-post-return"
```

**4 sample institutions (one row per major org type):**

```csv
institution_name,institution_type,cl_per_year,sl_per_year,el_per_year,el_carry_forward,el_encash_cap,maternity_weeks,paternity_days,comp_off_carry_forward,lwp_max_consecutive,special_remarks
"XYZ Engineering College (Hyderabad)","Engineering College",12,12,18,30,30,26,7,30,90,"Standard private engineering college; no clinical staff"
"ABC Medical College and Hospital (Chennai)","Combined (Medical + Paramedical)",12,12,24,30,30,26,15,30,90,"NMC-compliant; resident duty hour cap 48hrs/wk; clinical staff on shift roster"
"Delhi University — Faculty of Science (Delhi)","University (State)",12,12,30,300 (lifetime),30,26,15,30,180,"UGC-regulated; EL carry-forward 300 days lifetime; study leave up to 365 days per UGC"
"Lakeside Polytechnic (Coimbatore)","Polytechnic",12,12,15,30,15,26,7,30,90,"AICTE-affiliated; 24 day-boarding shifts; no research PhD staff"
```

**Validation column (notes for the HR Lead filling this CSV):**

| Column | Validation rule |
|---|---|
| `leave_type` | Unique across rows |
| `leave_type_code` | 2-8 chars, all uppercase, unique |
| `accrual_rate` | Numeric ≥ 0 |
| `accrual_period` | One of: `Monthly` / `Quarterly` / `Annual-lumpsum` / `Event-lumpsum` / `Per-occurrence` / `On-application` / `Weeks-lumpsum` / `Days-lumpsum` |
| `carry_forward_limit` | Numeric ≥ 0 |
| `max_consecutive_days` | Numeric > 0 |
| `encashment_allowed` | `Yes` / `No` |
| `encashment_cap_days` | Numeric ≥ 0; must be 0 if encashment is `No` |
| `medical_certificate_threshold_days` | Numeric ≥ 0 |
| `applicable_to` | Pipe-separated list from the 6 employee categories in A1 §2.1 |
| `approval_level` | One of: `L1-Manager` / `L2-HOD` / `L3-Principal` / `L3-Principal-plus-Chairman` |
| `notice_period_days` | Numeric ≥ 0 |

---

## 5. Edge Cases the Consultant Must Surface

| # | Edge case | Default behaviour | What to surface to the client |
|---|---|---|---|
| 1 | **Lapse vs carry-forward on CL** | Most Indian colleges lapse CL yearly | Check: 5-year-old CL claims by staff can become a litigation risk. Implement a hard carry-forward limit AND communicate it in the employee handbook. |
| 2 | **EL encashment on retirement** | Some colleges allow full encashment; others cap at 30 days | Cap is good for the college budget; employees negotiate. Document the policy in writing, signed by both parties. |
| 3 | **Maternity + EL stacking** | Some staff try to use 26 weeks ML + 18 days EL back-to-back | Establish whether ML is "inclusive of" or "exclusive of" EL. Most colleges allow EL after ML. |
| 4 | **Resident doctors' EL during NMC duty cap** | NMC cap = 48 hrs/wk averaged over 4 wks | Conflicting with leave scheduling. Surface the NMC compliance dashboard in Frappe HR. |
| 5 | **Comp Off for teaching staff on Sundays during exam duty** | Sunday exam duty = Comp Off | Teaching staff are often on call on Sundays. Make Comp Off accrual explicit and expiring in 90 days. |
| 6 | **LWP during probation** | Probation staff typically get less leave | Flag: extended LWP during probation may void confirmation. |
| 7 | **Sabbatical vs Study Leave** | Two different concepts | Sabbatical = college-initiated; Study Leave = employee-initiated for higher studies. Treat separately. |
| 8 | **Joining mid-year accrual** | Most colleges pro-rate | Need a Frappe HR Leave Policy Assignment with `effective_from` mid-year for the pro-ration to work. |
| 9 | **Negative leave balance** | Should be allowed for SL, NOT for CL | Configure `allow_negative = 1` for SL only. |
| 10 | **Holiday-list during leave** | Most colleges don't count holidays within leave as leave days | This is an HR Settings toggle: `include_holidays_in_total_leave_days = 0`. |

---

## 6. Sign-off

By signing below, the signatory confirms that the leave policy described in this form is the institution's current, valid policy, that it complies with the Indian labour laws cited in §3, and that the institution authorises Chronova to encode this policy in Frappe HR.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| HR Lead (form owner) | | | |
| Principal / Director | | | |
| Finance Officer (confirms encashment rules) | | | |
| Legal / Compliance Officer (optional) | | | |

**Form version:** v1.0 (2026-10-15)
**Status:** ✅ Ready for prospect use
**Owner:** Venkat Narasimha, Chronova

---

## Related

- [[A1-org-profile]] — Provides employee category counts that drive applicability
- [[A7-approval-matrix]] — Defines who approves each leave type's application
- [[B1-discovery-questionnaire]] — Phase 2 §3 walks through this form live with the client
- `knowledge/hr_payroll.md` — Reference on Leave Type / Leave Allocation DocType in Frappe HR

---

## Changelog

| Date | Changes |
|------|---------|
| 2026-10-15 | Initial v1.0 — 9 leave types with 9 attributes each, per-category applicability matrix, Indian regulatory anchors, 4 sample institutions (engineering, medical, university, polytechnic), 10 edge cases for consultant |
