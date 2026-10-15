# B — Spot-Check: A6 (Leave Policy) + A7 (Approval Matrix)

**Date:** 2026-10-15
**Reviewer:** Agent 4 (validation pass)
**Goal:** Identify concerns, missing fields, terminology drift, Indian-context gaps, and **cross-references** between A6 and A7 before the templates go to a real prospect.
**Severity scale:** **HIGH** = blocker for first prospect meeting · **MEDIUM** = fix before next template iteration · **LOW** = nice-to-have

---

## What this is
Side-by-side read of A6 (Leave Policy) and A7 (Approval Matrix) — the two largest client-facing templates — flagging everything that could embarrass Venkat in a live meeting or trip up the implementation engineer in Phase 3.

## Who reads it
- **Venkat** — decides which findings to fix now vs. defer
- **Implementation engineer** — uses findings to set prospect expectations correctly
- **Agent 1 / Agent 2** (originators) — incorporate fixes into v1.1

---

## A6 — Leave Policy findings

| # | Finding | Severity | Source |
|---|---------|:---:|---|
| A6-1 | **Maternity Leave — 3rd-child rule not captured in CSV.** §1.4 and §3 state the 26-wk / 12-wk split, but the CSV has only one row `ML-Maternity` with `accrual_rate=26, Weeks-lumpsum`. A college with 3rd-child pregnancy will either get 26 weeks (over-grant) or fail to apply the 12-week rule. | **HIGH** | A6 §1.4 + CSV row 4 |
| A6-2 | **Paternity Leave defined in 3 places.** (i) §1.4 as `ML — Paternity` with 7 days; (ii) §1.8 sub-categories as `Paternity 7-15 days`; (iii) CSV as `ML-Paternity 7 days` **and** `SPL-PT 15 days`. Confusing for a college HR Lead. Recommend a single Paternity row (7-15 days, configurable) and remove the duplicate. | **HIGH** | A6 §1.4 + §1.8 + CSV |
| A6-3 | **Income Tax exemption limit may be stale.** §3 row cites *"Encashed leave up to ₹25,00,000 in a year is exempt from tax (old regime; check current rules)"*. Budget 2023 amended Section 10(10AA) — non-Government employees lost the ₹25L exemption. Verify with current CA before sending to first prospect. | **HIGH** | A6 §3 regulatory anchors |
| A6-4 | **§1.9 is intentionally blank** — "Comp Off — Reference (already covered in 1.5). This entry is intentionally blank to preserve numbering." Confusing — looks like a missing section. Either remove the §1.9 heading or add a forward-pointer only. | **LOW** | A6 §1.9 |
| A6-5 | **Sub-categories gap in CSV vs §1.8.** §1.8 lists 8 sub-categories (Bereavement, Marriage, Paternity, Adoption, Study, Jury, Sports). CSV has 4 special-leave rows: Bereavement, Marriage, Paternity-Extended, Study. **Missing: Adoption, Jury, Sports** (and the §1.8 sub-categories table does not have a `max_subcat_days` cap per subcategory in CSV). | **MEDIUM** | A6 §1.8 vs CSV |
| A6-6 | **"Teaching Visiting" employee category in applicability matrix but not in CSV `applicable_to` allowed list.** §2 matrix shows `Teaching Visiting` as a column, but CSV's `applicable_to` only enumerates `Teaching\|NT-Academic\|Medical\|Paramedical\|Admin\|Support` (6 categories). Visiting faculty either get lumped into "Teaching" (wrong entitlement) or fall out of every leave type. | **MEDIUM** | A6 §2 vs CSV validation |
| A6-7 | **EL carry-forward inconsistency in applicability matrix.** §2 shows `EL: Teaching FT 18/yr, 30 CF` but `Paramedical: 18/yr` (no CF stated). The table is read as "everything in the row applies" — missing CF number suggests paramedical cannot carry forward EL. Either fill in the CF for every category or add a footnote that "no number = default 30". | **MEDIUM** | A6 §2 applicability matrix |
| A6-8 | **`accrual_basis` not in CSV schema.** §1.3 EL allows *"1.5 days per month"* OR *"1 day per 20 days worked"*. Frappe HR distinguishes these (calendar-month vs. days-worked), but CSV has no `accrual_basis` column. The Frappe HR mapping at the bottom of §1.3 hardcodes `earned_leave_frequency=Monthly` — will be wrong for Factories-Act-style accrual. | **MEDIUM** | A6 §1.3 + CSV schema |
| A6-9 | **CSV `frappe_hr_setup_notes` is free text.** Hard to validate programmatically; semicolon-separated key=value. Recommend a structured child table in v1.1. | **LOW** | A6 §4 CSV schema |

---

## A7 — Approval Matrix findings

| # | Finding | Severity | Source |
|---|---------|:---:|---|
| A7-1 | **SLAs mix hours and business-days without unit standardisation.** §2.1 Leave = 24h/level. §2.2 OD = 48h. §2.3 Shift = 12h. §2.4 Comp Off = 48h. §2.5 Att Reg = 24h. §2.6 Tour = 72h. §2.7 Loan = 5 working days (CSV = 120h). §2.8 Reimb = 7 working days (CSV = 168h). §2.9 Medical = 10 working days (CSV = 240h). §2.10 Resign = 30 days (CSV = 720h). Either: (a) make all SLAs in calendar-hours and add a `business_hours_only` flag, or (b) state working-hours-per-day (e.g., 8 h × 5 days = 40 h/week) in §1. | **MEDIUM** | A7 §2 + CSV |
| A7-2 | **L4 (Chairman) thresholds inconsistent across document types.** §1 example engineering college: Chairman for `> ₹5 lakh`. §2.6 Tour: `> ₹50,000`. §2.7 Loan: `> ₹1L`. §2.8 Reimb: `> ₹50K`. §2.9 Medical: `> ₹1L`. **Four different Chairman thresholds in one matrix** — either consolidate into a single "L4 threshold matrix" table or call out the variance explicitly. | **HIGH** | A7 §1 vs §2.6–§2.9 |
| A7-3 | **§1 says L4 is "Optional, for high-impact" but §2.6–§2.9 all require L4.** Either L4 is always required (and the "optional" language is wrong) or §2.6–§2.9 are wrong. Pick one. | **MEDIUM** | A7 §1 + §2.6–§2.9 |
| A7-4 | **§2.7 Loan SLA unit confusion.** Body says *"5 working days"*, CSV says `sla_hours_L1=120`. 5 working days = 5×8h = 40h (business hours) OR 5×24h = 120h (calendar hours). The CSV chose 120h, but the consultant will read "5 days" and assume the 5th day is when SLA expires. Spell out the unit. | **MEDIUM** | A7 §2.7 + CSV |
| A7-5 | **§2.10 Resignation "auto-acknowledge" + 720h SLA contradict.** L1 and L2 are documented as *"auto-acknowledgement (system-driven)"* in the Frappe HR setup note, but the CSV SLA shows 720h at L1 and L2. Auto-ack should be 0h SLA. | **MEDIUM** | A7 §2.10 + CSV |
| A7-6 | **§2.9 Medical — ESIC/CGHS coordination is manual.** The note says *"the medical reimbursement must be processed AFTER the ESIC/CGHS claim"*, but no workflow step enforces it. HR will forget → over-payment. Build a `is_cghs_esic_residual` check or a workflow precondition. | **HIGH** | A7 §2.9 + Frappe HR setup |
| A7-7 | **§2.4 Comp Off — custom DocType is significant work.** The Frappe HR setup says *"Custom DocType `Compensatory Off Application` (NOT a Leave Application)"* but Frappe HR's stock `Compensatory Leave Request` DocType exists. Building a custom DocType = +1 week per tenant. Reconsider using stock unless the customisation is essential. | **MEDIUM** | A7 §2.4 + Frappe HR setup |
| A7-8 | **§2.1 Leave — "Skip to L3 if > 5 days" ambiguity.** Says *"> 5 consecutive days: skip to L3"*, but the workflow is L1→L2→L3. "Skip" means bypass L1 and L2 and start at L3? Or short-circuit L3's auto-approval? Clarify in v1.1 — this is a common failure mode in leave workflows. | **MEDIUM** | A7 §2.1 |
| A7-9 | **CSV missing `campus` column for multi-campus institutions.** §4 explicitly says *"For multi-campus institutions, one set of rows per campus"* — but the schema has no `campus` column. The HR Lead will have to maintain separate CSV files manually. | **MEDIUM** | A7 §4 |
| A7-10 | **§2.5 Attendance Regularization — "L2 NOT REQUIRED" is a workflow hole.** Single-day regularization goes L1→HR, no L2. What happens when L1 is the same person as the applicant (e.g., a HOD regularizing their own punch)? Frappe HR's `prevent_self_approval` blocks it, but the doc doesn't say so. | **LOW** | A7 §2.5 |

---

## A6 ↔ A7 cross-reference findings

The biggest risk class: the two templates were written somewhat independently and use **"approval level"** with two different semantics.

| # | Finding | Severity | Source |
|---|---------|:---:|---|
| X-1 | **"Approval level" means FINAL approver in A6, but FULL CHAIN in A7.** A6 §1.3 says EL Approval = `L2 — HOD`. A7 §2.1 routes Leave Application through L1, L2, L3 for **all** leave types. So is EL approved at L2 only (A6's reading) or must reach L3 (A7's reading)? Pick one semantic and standardise across both docs. | **HIGH** | A6 §1.3 + A7 §2.1 |
| X-2 | **Maternity / LWP / Special Leave — A6 says L3, A7 chains through L1+L2+L3.** A6 §1.4 ML Approval = `L3 Principal`. A6 §1.6 LWP = `L3 Principal`. A6 §1.8 Special = `L3 Principal`. A7 §2.1 routes **all** leave through L1+L2+L3. A prospect reading A6 will think Maternity needs only Principal sign-off; A7 contradicts that. | **HIGH** | A6 §1.4, §1.6, §1.8 vs A7 §2.1 |
| X-3 | **Sick Leave escalation rule contradicts its own A6 row.** A6 §1.2 SL: Approval level = `L1 — Immediate Manager`, but the **Notes** column says *"For >3 consecutive days, escalate to L2 (HOD)"*. A6's row says L1; the escalation says L2. A7 §2.1 has no auto-escalation logic. Document a single rule. | **HIGH** | A6 §1.2 + A7 §2.1 |
| X-4 | **Comp Off — A6 says L2+HR; A7 says L1+L2+HR.** A6 §1.5 Comp Off Approval = `L2 HOD + L3 HR confirmation`. A7 §2.4 Comp Off = `L1 Manager → L2 HOD → L3 HR`. These match if A6's "L2+HR" is shorthand for "L1+L2+HR" — but the shorthand is not explained. | **MEDIUM** | A6 §1.5 vs A7 §2.4 |
| X-5 | **OD — A6 says L2+Principal; A7 says L1+L2+Principal.** A6 §1.7 OD Approval = `L2 HOD + L3 Principal`. A7 §2.2 OD = `L1 Manager → L2 HOD → L3 Principal`. Same shorthand issue as X-4. | **LOW** | A6 §1.7 vs A7 §2.2 |
| X-6 | **CSV `approval_level` is a single value but A7 matrix is multi-level.** A6 CSV has one `approval_level` column. A7 CSV has `L1_role, L2_role, L3_role, L4_role`. The A6 CSV cannot capture a 3-level chain — only the FINAL approver. This is a structural mismatch between the two CSV schemas. | **MEDIUM** | A6 CSV + A7 CSV |

---

## Indian-context gaps

| # | Finding | Severity | Source |
|---|---------|:---:|---|
| IC-1 | **NMC resident duty-hour cap (48 hrs/wk) not built into the Leave Type.** A6 §3 mentions it; A6 §5 edge case #4 surfaces it; but no Leave Type has a *"max_hours_per_week"* enforcement. A clinical college's compliance audit will fail. | **MEDIUM** | A6 §3, §5.4 |
| IC-2 | **UGC study leave for faculty — 365 days cap, 2-year bond.** A6 §1.8 Special-Study mentions this in the §1.8 table, but CSV `Special Leave Study` row's `frappe_hr_setup_notes` is the only place the bond-period is captured. No separate "bond tracking" field. | **LOW** | A6 §1.8 + CSV |
| IC-3 | **No field for "blood group" / "emergency contact" for hospital clients.** Hospital HR forms typically capture this. May be in A1 — verify. If not, add to A1 CSV. (Out of A6/A7 strict scope, flagging as cross-template gap.) | **LOW** | (likely A1 §2.1) |
| IC-4 | **No field for ESI eligibility threshold (salary < ₹21,000/mo).** A7 §2.9 mentions ESIC coordination but the threshold is not captured as a per-employee field. (Likely A1.) | **LOW** | A7 §2.9 |

---

## CSV schema cross-cutting concerns

| # | Finding | Severity | Source |
|---|---------|:---:|---|
| CSV-1 | **A6 and A7 CSVs cannot be joined.** They have different primary keys (A6 = `leave_type`, A7 = `document_type`) and no shared `institution_id` or `tenant_slug` field. A reporting query like "leave-type X's approver chain for tenant Y" requires a manual join. Add a `tenant_slug` column to both. | **MEDIUM** | A6 §4 + A7 §4 |
| CSV-2 | **Validation column at the bottom of A6 CSV is good (12 rules) but A7 CSV validation column is only 7 rules.** A6 has 12 validation rules; A7 has 7. A7's `L1_role` is "Free text" — looser than A6's enum. Standardise. | **LOW** | A6 §4 + A7 §4 |
| CSV-3 | **No CSV-level unique-key constraint documented.** If a college re-uploads the CSV, will duplicate rows be rejected or merged? `tenant_seed.py` should be idempotent on the unique key. | **LOW** | A6 + A7 §4 |

---

## Summary — Top 5 must-fix before first prospect

1. **A6-1 (HIGH)** — Maternity 3rd-child rule not in CSV
2. **X-1 (HIGH)** — "Approval level" semantic drift between A6 and A7
3. **X-2 (HIGH)** — Maternity / LWP / Special Leave route-through contradiction
4. **A7-2 (HIGH)** — L4 Chairman threshold inconsistency across 4 document types
5. **A7-6 (HIGH)** — ESIC/CGHS coordination is manual; no workflow enforcement

**Total findings:** 28 (10 A6 + 10 A7 + 6 X-ref + 4 Indian-context + 3 CSV-schema; 8 HIGH, 14 MEDIUM, 6 LOW)

---

*See also: `A-verification.md` (B1 default decisions); `C-review-packet.md` (architecture working session).*
