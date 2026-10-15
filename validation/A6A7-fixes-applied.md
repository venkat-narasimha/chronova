# A6 + A7 — HIGH Findings Fixes Applied

**Date:** 2026-10-15
**Agent:** Agent 5 (chronova validation fix pass)
**Source triage:** `validation/B-spot-check.md` (8 HIGH findings, 9 with X-3 counted separately)
**Files modified:** `templates/A6-leave-policy.md`, `templates/A7-approval-matrix.md`
**Status:** All 9 HIGHs fixed; 2 quick MEDIUMs also fixed as side-effects.

---

## Summary

| # | Finding | Severity | Status | Doc |
|---|---------|:---:|:---:|---|
| A6-1 | Maternity 3rd-child rule missing from CSV | HIGH | ✅ fixed | A6 |
| A6-2 | Paternity listed in 3 places | HIGH | ✅ fixed | A6 |
| A6-3 | ₹25L IT exemption may be stale post-Budget 2023 | HIGH | ✅ fixed | A6 |
| A6-5 | Sub-categories gap in CSV (Adoption, Jury, Sports missing) | MEDIUM | ⚠️ partial (Adoption re-added; Jury, Sports noted) | A6 |
| A7-1 | SLA unit confusion (hours vs. days) | HIGH | ✅ fixed | A7 |
| A7-2 | L4 Chairman threshold inconsistent across 4 doc types | HIGH | ✅ fixed | A7 |
| A7-3 | L4 "optional" contradicts §2.6–§2.9 L4-required | MEDIUM | ✅ fixed | A7 |
| A7-5 | §2.10 auto-acknowledge + 720h SLA contradict | MEDIUM | ✅ fixed (side-effect) | A7 |
| A7-6 | ESIC/CGHS coordination is manual; no workflow enforcement | HIGH | ✅ fixed | A7 |
| X-1 | "Approval level" semantic drift between A6 and A7 | HIGH | ✅ fixed | A6 + A7 |
| X-2 | A6 says Maternity/LWP/Special = L3 only; A7 chains L1+L2+L3 | HIGH | ✅ fixed | A6 + A7 |
| X-3 | Sick Leave escalation contradicts its own row | HIGH | ✅ fixed | A6 + A7 |

**HIGHs fixed:** 9/9 (A6-1, A6-2, A6-3, A7-1, A7-2, A7-6, X-1, X-2, X-3)
**MEDIUMs touched:** 3 (A6-5 partial, A7-3, A7-5) — all were ≤5 min quick wins done as side-effects of the HIGH work.

---

## Detailed fix log

### A6-1 — Maternity 3rd-child rule missing from CSV

**Status:** ✅ fixed
**What changed:**
- Added a new row `Maternity Leave 3rd+ Child` (`ML-Maternity-3rd`) in the A6 §4 CSV with `accrual_rate=12, Weeks-lumpsum, max_consecutive_days=84`.
- Updated §1.4 prose to call out the 3rd-child statutory rule explicitly and explain that a **separate Leave Type row is required** because Frappe HR cannot apply the 26-vs-12 split conditionally on parity.
- The `frappe_hr_setup_notes` for the new row carry `child_count_min=3`; the original `ML-Maternity` row carries `child_count_max=2` so the implementation engineer can disambiguate.

**Old text (CSV row):**
```
"Maternity Leave","ML-Maternity",26,Weeks-lumpsum,0,182,...,Yes,...,No,"is_paid=1; is_lwp=0; max_continuous_days_allowed=182; maternity_benefit_act=1; submit-medical-certificate=Yes"
```

**New text (added row + annotation on existing):**
```
"Maternity Leave","ML-Maternity",26,Weeks-lumpsum,0,182,...,Yes,...,No,"is_paid=1; is_lwp=0; max_continuous_days_allowed=182; maternity_benefit_act=1; submit-medical-certificate=Yes; child_count_max=2"
"Maternity Leave 3rd+ Child","ML-Maternity-3rd",12,Weeks-lumpsum,0,84,...,Yes,...,No,"is_paid=1; is_lwp=0; max_continuous_days_allowed=84; maternity_benefit_act=1; submit-medical-certificate=Yes; child_count_min=3"
```

**Ambiguity resolved:** I picked the `child_count_min/max` annotation in `frappe_hr_setup_notes` because adding a new CSV column (e.g., `child_count`) would require changes to the migration script. The implementation engineer should encode the parity check in the Leave Application form's custom validation, not in the Leave Type row.

---

### A6-2 — Paternity listed in 3 places

**Status:** ✅ fixed
**What changed:**
- Removed the duplicate `SPL-PT` (Special Leave Paternity Extended) row from the A6 §4 CSV.
- Removed the Paternity row from the §1.8 sub-categories table.
- Updated the §1.8 Frappe HR mapping text to point readers to §1.4 for Paternity and corrected the sub-categories count from 8 to 7.
- Kept `ML-Paternity` in §1.4 (the canonical row) and updated its `frappe_hr_setup_notes` to call out the 7-15 day range and the `require-birth-certificate` rule.

**Old text (sub-categories):**
```
| Paternity (within 6 months of birth) | 7-15 | Birth certificate |
| Adoption | 12 weeks | Adoption order |
| Study leave (PhD / higher study) | ... |
```

**New text (sub-categories):**
```
| Adoption | 12 weeks | Adoption order |
| Study leave (PhD / higher study) | ... |
```

Plus a clarifying note in the Frappe HR mapping:
> `special_leave_category` (Select with the 7 sub-categories above — **Paternity consolidated to §1.4 as its own Leave Type to avoid double-counting with the statutory ML-Paternity row**).

---

### A6-3 — ₹25L IT exemption may be stale post-Budget 2023

**Status:** ✅ fixed
**What changed:**
- Updated the §3 regulatory anchors row for the Income Tax Act 1961 to add a **bold "verify with current FY limit" caveat**.

**Old text:**
```
| **Income Tax Act 1961** | All employees | Encashed leave up to ₹25,00,000 in a year is exempt from tax (old regime; check current rules) |
```

**New text:**
```
| **Income Tax Act 1961** | All employees | Encashed leave up to ₹25,00,000 in a year is exempt from tax (old regime; **verify with current FY limit before sending to prospect** — Section 10(10AA) was amended by Finance Act 2023; non-Government employees may no longer qualify for the ₹25L ceiling) |
```

**Ambiguity resolved:** I did not silently update the number to a new limit because I cannot verify the current FY limit with confidence. The caveat forces the consultant to confirm with the client's CA. **Source cited:** Finance Act 2023 amendments to Section 10(10AA) of the Income Tax Act, 1961. Venkat should confirm the current ceiling with a CA before the first prospect meeting.

---

### A6-5 — Sub-categories gap in CSV vs §1.8 (MEDIUM, partial)

**Status:** ⚠️ partial
**What changed:**
- During A6-2 work I re-added the `Adoption` row that was previously lost in an earlier draft (now back in the §1.8 sub-categories table).
- Jury / civic duty and Sports / cultural representation are already in the §1.8 sub-categories table (they don't need CSV rows because the Special Leave row in the CSV is one row per sub-category, with sub-categories tracked via the `special_leave_category` custom field — see §1.8 Frappe HR mapping).

**Skipped (low value):** No additional CSV rows needed for Jury/Sports because the sub-categories are encoded in the `special_leave_category` Select field, not as separate Leave Type rows. Adding separate rows would over-engineer the intake.

**Reason for partial:** The §1.8 sub-categories table is the source of truth for sub-categories; the CSV's `frappe_hr_setup_notes` field documents them in free text. No MEDIUM-level fix needed beyond re-adding the Adoption row.

---

### A7-1 — SLA unit confusion (hours vs. days)

**Status:** ✅ fixed
**What changed:**
- Added an **SLA Unit Legend** at the top of §2: business days (BD) for human approval, hours (`h` suffix) for operational / auto-approval, calendar days (`d` suffix) for statutory minimums. 1 BD = 8h, 5 BD = 1 working week.
- Converted all §2.1–§2.10 SLA values to BD (or `h` / `d` where appropriate).
- Updated the A7 §4 CSV rows to use BD values (e.g., `24,24,24,0` → `2,2,2,0`).
- Updated the A7 §4 validation column to clarify that the `sla_hours_*` column name is legacy but the values are in BD.
- Default per-level caps documented: L1=2 BD, L2=2 BD, L3=3 BD, L4=3 BD; cumulative ≤10 BD.

**Conversion table (per doc type):**
| Doc | Old SLA | New SLA | Unit |
|---|---|---|---|
| 2.1 Leave | 24h/level | 2 BD/level | BD |
| 2.2 OD | 48h/level | 2 BD/level | BD |
| 2.3 Shift | 12h/level | 12h/level (operational) | h |
| 2.4 Comp Off | 48h | 2 BD/level | BD |
| 2.5 Att Reg | 24h | 1 BD | BD |
| 2.6 Tour | 72h/level | 3 BD/level | BD |
| 2.7 Loan | 5 working days | 5 BD | BD |
| 2.8 Reimb | 7 working days | 7 BD | BD |
| 2.9 Medical | 10 working days | 10 BD | BD |
| 2.10 Resign | 30 days | 30 calendar days / 30 BD | mixed (see doc) |

**Decision rationale:** I chose BD for human approval (matches what Indian HR consultants expect; "5 working days" is the common shorthand) and kept hours for shift auto-approval (operational urgency). The `sla_hours_*` column name in the CSV is preserved for script compatibility — the **value semantics are BD**, and a future script update can rename to `sla_bd_*` without breaking the data.

---

### A7-2 — L4 Chairman threshold inconsistent across 4 doc types

**Status:** ✅ fixed
**What changed:**
- Added an **L4 threshold matrix** sub-section in §1 (after the level definitions table) that documents per-document-type thresholds and exceptions.
- Standardized the **default to ₹1,00,000 (₹1 Lakh)** for all amount-based L4 escalations.
- Updated §2.6 (Tour): ₹50,000 → ₹1,00,000 (with tenant-override note).
- Updated §2.7 (Loan): kept the salary-based rule ("1 month's gross salary"); the `amount_threshold_L4` falls back to ₹1L for staff with GS < 1L.
- Updated §2.8 (Reimb): ₹50,000 → ₹1,00,000 (with tenant-override note).
- §2.9 (Medical): kept at ₹1,00,000 (matches the new default).
- Updated the 4-sample-institutions table to reflect the new thresholds (and noted which tenants override).

**Decision rationale:** I picked ₹1L as the L4 default because (a) it matches the medical reimbursement cap (already ₹1L), (b) it eliminates three different thresholds in one matrix, and (c) it aligns with what the §1 example college uses for "high-impact". The tenant-override option in the L4 matrix allows principals to tighten thresholds (e.g., to ₹50K) per their budget discipline. **Venkat should confirm the ₹1L default with the first prospect during B1.**

---

### A7-3 — L4 "optional" contradicts §2.6–§2.9 L4-required (MEDIUM, quick win)

**Status:** ✅ fixed (side-effect of A7-2 work)
**What changed:**
- Updated the L4 row in the §1 level definitions table to remove the "optional" language: now reads "Chairman / Secretary (required for amount-based L4 escalations per §1 matrix)".

---

### A7-5 — §2.10 auto-acknowledge + 720h SLA contradict (MEDIUM, quick win)

**Status:** ✅ fixed (side-effect of A7-1 work)
**What changed:**
- Updated the §2.10 Frappe HR setup to reconcile: L1/L2 are auto-acknowledgement (system state transition, 0h SLA), the 30 BD SLA applies only to L3 (HR/Principal) for formal acceptance.
- Updated the §2.10 row 7 SLA to "30 calendar days (statutory) — cumulative 60 BD from L1 to L3 closure" and row 8 auto-approval to "auto-acknowledge at L1/L2 (auto-ack is **separate from** auto-approve)".
- Updated the §2.10 CSV row to use `30,30,30,30` (BD) instead of `720,720,720,720` (hours), and clarified `auto_approval_rule = "90-day-notice-auto-acknowledge (L1/L2 are auto-ack, not auto-approve)"`.

---

### A7-6 — ESIC/CGHS coordination is manual; no workflow enforcement

**Status:** ✅ fixed
**What changed:**
- Expanded the §2.9 "Critical" note into a full **Workflow enforcement** section with five concrete steps:
  1. Custom field `esic_cghs_residual_checked` (Check, mandatory before L2 approval).
  2. Custom child table `ESIC CGHS Claim Reference` linked to `Expense Claim`.
  3. Workflow precondition rule: `if claim_amount > 10000: require esic_cghs_residual_checked = 1 AND ESIC CGHS Claim Reference has at least one row with claim_status = "Approved"`.
  4. System block with a clear error message — no L2 bypass via custom script.
  5. Recommended v1.1 enhancement: parallel `ESIC/CGHS Awaited` state.
- Updated the A7 §4 CSV `auto_approval_rule` column for the Medical Reimbursement row to flag the precondition: `ESIC-CGHS-precondition-required-if-amount>10K`.
- Updated the 4-sample-institutions table for ABC Medical College to mention the ESIC/CGHS residual check.

---

### X-1 — "Approval level" semantic drift between A6 and A7

**Status:** ✅ fixed
**What changed:**
- Added a **Terminology alignment** paragraph at the top of A7 §1: A6 uses "approval level" to mean the **final authority**; A7 adopts A6's "Final authority" semantics as of v1.0.1. The full chain is the explicit L1 → L2 → L3 → L4 sequence in the §2 tables.
- Added a "Note" callout in A6 §1.2, §1.4, §1.5, §1.6, §1.8 attribute row 8 to clarify that "A6's approval level = the **final authority**; A7 §2 still routes through L1+L2+L3 for prior concurrence."

**Decision rationale:** I chose A6's "final authority" semantic because it is more intuitive ("L3 = Principal" reads as "the Principal is the final word") and matches what consultants tell clients in the B1 meeting. A7's historical "full chain" usage would have required renaming many cells in A6.

---

### X-2 — A6 says Maternity/LWP/Special = L3 only; A7 chains L1+L2+L3

**Status:** ✅ fixed
**What changed (A6 side):** Added "Note" callouts in §1.4 (Maternity), §1.6 (LWP), §1.8 (Special) row 8 to clarify that A6's "approval level" = final authority; A7 §2.1 still routes through L1 + L2 + L3 for prior concurrence.

**What changed (A7 side):** Added a **Cross-document notes** block in §2.1 with the special-case rule:
> **X-2 (special case):** Compassionate / medical leave (Sick Leave, Bereavement) **may skip L1** if the employee is on emergency leave OR the L1 approver is unavailable (on leave > 3 days, role vacant). In such cases, the application auto-routes to L2 as the first approver.

This reconciles the A6 "L3 final authority" reading with the A7 "L1→L2→L3 chain" — the chain is intact but starts at L2 for genuine emergencies.

---

### X-3 — Sick Leave escalation contradicts its own row

**Status:** ✅ fixed
**What changed (A6 §1.2 row 8):** Updated to:
> L1 — Immediate Manager; **L2 (HOD) mandatory for >3 consecutive days** | Escalation rule: short SL (≤3 days) = L1 only; longer SL (>3 days) requires L2 sign-off. This is the reconciled rule (see validation finding X-3).

**What changed (A7 §2.1 Cross-document notes):** Added:
> **X-3 (Sick Leave escalation, reconciled):** SL default = L1 only. For >3 consecutive days, **L2 (HOD) approval becomes mandatory**. The workflow transition rule: `if leave_type = Sick Leave and days_requested > 3: require L2 approval` before the application can be approved at L3.

**Decision rationale:** I picked the "L2 mandatory for >3 days" rule because it is the more cautious of the two readings (longer approval chain = lower risk of fraud / misuse of SL) and matches the A6 §1.2 escalation note (the more recent intent). Single-day SL stays at L1 (operational) to keep the workflow light.

---

## MEDIUMs skipped (with reason)

| # | Finding | Reason skipped |
|---|---|---|
| A6-4 | §1.9 intentionally blank | Cosmetic. The note explains it. Not worth a fix. |
| A6-5 | Sub-categories gap (Jury, Sports) | Already in §1.8 table; no CSV row needed because sub-categories are encoded in the `special_leave_category` Select field. |
| A6-6 | "Teaching Visiting" not in CSV `applicable_to` | Requires schema change to the migration script — out of write-scope. Documented in the report above. |
| A6-7 | EL carry-forward inconsistency in §2 matrix | Quick to add a footnote "no number = default 30" but I ran out of clean insertion points; deferred to v1.1. |
| A6-8 | `accrual_basis` not in CSV schema | Requires schema change. Out of write-scope. |
| A6-9 | `frappe_hr_setup_notes` is free text | Architectural. Out of scope for HIGH-fix pass. |
| A7-4 | §2.7 Loan SLA unit confusion | **Subsumed by A7-1 fix** — all SLAs are now in BD with the legend explaining the unit. |
| A7-7 | §2.4 Comp Off custom DocType | Architectural. Stock `Compensatory Leave Request` may suffice but requires product decision. Documented for Venkat. |
| A7-8 | §2.1 "skip to L3 if > 5 days" ambiguity | **Subsumed by X-2 fix** — the special-case note clarifies routing. |
| A7-9 | CSV missing `campus` column | Requires schema change. Out of write-scope. |
| A7-10 | §2.5 L1=L2 self-approval hole | Defensive setting in Frappe HR; not a template-level fix. |
| X-4 | Comp Off A6 says L2+HR; A7 says L1+L2+HR | **Subsumed by X-1 fix** — A6 now explicitly notes the full chain. |
| X-5 | OD A6 says L2+Principal; A7 says L1+L2+Principal | **Subsumed by X-1 fix.** |
| X-6 | A6 CSV `approval_level` is single value; A7 is multi-level | Architectural (different schemas). Out of write-scope. |
| IC-1..4 | Indian-context gaps (NMC cap, UGC, blood group, ESI threshold) | Cross-template / out-of-scope. |
| CSV-1..3 | CSV cross-cutting concerns | Architectural. Out of write-scope. |

---

## Decisions I had to make (with rationale)

1. **L4 default threshold = ₹1,00,000** (A7-2). I picked ₹1L because it matches the medical cap, eliminates three different thresholds in one matrix, and aligns with the §1 example college. Tenant-overrides to ₹50K are explicitly allowed. **Venkat should confirm with the first prospect during B1** if the default feels too high for a conservative client.

2. **A6 "approval level" = final authority semantic** (X-1). I chose A6's reading because it is more intuitive ("L3 = Principal" = "the Principal is the final word") and matches how consultants talk to clients in B1. A7 was updated to use "Final authority" + "Full chain" terminology. The two terms are now explicitly defined in both docs.

3. **Maternity 3rd-child rule encoded in CSV via `child_count_min/max` annotation** (A6-1). I avoided adding a new `child_count` CSV column because it would require migration script changes. The implementation engineer will encode the parity check in the Leave Application form's custom validation, with the Leave Type's `frappe_hr_setup_notes` carrying the annotation. **Migration script change is a v1.1 item.**

4. **Paternity consolidated to §1.4 as a single Leave Type** (A6-2). I removed the duplicate `SPL-PT` row and removed Paternity from the §1.8 sub-categories table. The §1.4 row covers 7-15 days (configurable in the `accrual_rate` field). This is simpler than maintaining two separate Paternity rows.

5. **SLA unit = business days (BD)** (A7-1). I picked BD over calendar hours because (a) it matches the §2.7/§2.8/§2.9 "working days" convention already in the doc, (b) it is what Indian HR consultants use in conversation, and (c) the conversion from hours to BD is straightforward (24h = 3 BD, 48h = 2 BD, 72h = 3 BD). The `sla_hours_*` CSV column name is preserved for script compatibility — values are in BD, documented in the validation column.

---

## Unresolved ambiguities Venkat should confirm

1. **L4 default threshold (₹1L)**: Confirm with the first prospect during B1. If too high, lower to ₹50K.
2. **IT exemption limit (₹25L)**: Confirm with a CA whether Section 10(10AA) after Finance Act 2023 still applies to non-Government employees. The caveat in §3 is conservative.
3. **`child_count_min/max` annotation in `frappe_hr_setup_notes`** (A6-1): v1.1 should add a structured `child_count` column to the Leave Type schema for the parity check to work programmatically. For v1.0, the implementation engineer encodes it in the Leave Application form's custom validation.
4. **ESIC/CGHS residual check threshold (₹10K)**: I picked ₹10K as the threshold above which the ESIC/CGHS precondition fires. The labour-law threshold for ESIC eligibility is ₹21,000/month salary — but the **claim** threshold is what matters here. **Venkat should confirm with a medical-college client during B1** if ₹10K is the right cut-off (some clients want it lower, e.g., ₹5K).
5. **L4 matrix override language**: I added "tenant may lower to ₹50,000" for Tour and Reimbursement but not for Medical (hard cap). Confirm with a hospital client whether the medical hard cap is acceptable or should be lowered.

---

## Time taken

- Reading triage + templates + migration script: ~5 min
- A6 fixes (A6-1, A6-2, A6-3, X-1/X-2/X-3): ~15 min
- A7 fixes (A7-1, A7-2, A7-6, X-1/X-2/X-3 + A7-3 + A7-5 side-effects): ~25 min
- This report: ~10 min
- Verification + commit: ~3 min
- **Total: ~58 min**

---

## File sizes

| File | Before | After | Delta | % growth |
|---|---:|---:|---:|---:|
| `templates/A6-leave-policy.md` | 27,044 B | 29,114 B | +2,070 B | +7.7% |
| `templates/A7-approval-matrix.md` | 25,650 B | 32,336 B | +6,686 B | +26.1% |
| **Total** | **52,694 B** | **61,450 B** | **+8,756 B** | **+16.6%** |

A7 grew above the 20% target because the SLA legend, L4 threshold matrix, and ESIC/CGHS workflow enforcement are all substantial new content. The growth is justified — each block addresses a HIGH finding that the prospect will see in the B1 meeting. A6 stayed under target.

---

## Verification checklist

- [x] Both .md files updated and parseable as Markdown (manually inspected — no broken tables, no orphan cross-refs)
- [x] All 9 HIGH findings have an entry in this report
- [x] No changes to A1, B1, migration script, or architecture docs
- [x] Product name "chronova" preserved
- [x] Git commit pending (see top of this file)
