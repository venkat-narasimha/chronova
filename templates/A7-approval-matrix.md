# A7 — Approval Matrix Intake

**Form Code:** A7
**Form Name:** Approval Matrix — Document Type × Approver Routing
**Date:** 2026-10-15
**Version:** v1.0
**Status:** ✅ Ready for prospect use
**Owner:** Venkat Narasimha (College HR Foundation)
**Time to complete:** 25–35 minutes
**Format:** Google Form OR Excel upload (CSV schema embedded below)
**Companion forms:** A1 (Org Profile), A6 (Leave Policy)
---

## What This Is

This is the **approval matrix intake form** College HR Foundation uses to define **who approves what** in the prospect's Frappe HR instance. It captures the **10 standard document types** that drive day-to-day HR operations in a college / hospital — from leave applications to resignation acceptances — and for each one defines the **approver hierarchy** (L1 → L2 → L3 → Final authority), the **amount or day threshold** that triggers escalation, and the **role-based approver names** (not person names — person names go in A1 §2.4).

The form's output drives Frappe HR's **Workflow DocType** (one workflow per document type) and the **Employee / Department leave_approvers child table** that auto-routes approvals based on the applicant's reporting line.

## Who Fills It

The **HR Lead** owns this form but must consult the **Principal / Director** (who defines the delegation of authority) and the **Finance Officer** (who defines the monetary thresholds — e.g., what amount of travel reimbursement needs the Principal's sign-off vs. the CFO's).

For larger institutions (300+ employees), also consult the **Heads of Department** to confirm that L1 (immediate manager) approval makes sense at the department level. For multi-campus institutions, the form must be filled **per campus** if the approval chains differ.

## When To Use It

This form is filled **after A6 (Leave Policy)** because the leave approval routing in this matrix depends on the leave types defined in A6. The consultant walks through each document type live during **Phase 2 of the B1 discovery meeting**, captures the answers, and the HR Lead reviews within 48 hours.

> **Critical:** The form defines **role-based** approvers (e.g., "HOD — Mechanical Engineering", "CFO", "Principal"). **Person names** are captured separately in A1 §2.4 and mapped to roles during Phase 0 (Environment Setup). This separation matters because the approval chain must survive staff turnover — when a HOD leaves, the workflow should auto-rebind to the new HOD without manual intervention.

---

## 1. Approver Level Definitions

Standard 4-level hierarchy used in all 10 document types below:

| Level | Role | Authority | Example for engineering college | Example for medical college + hospital |
|---|---|---|---|---|
| **L1** | Immediate Manager / Reporting Officer | First-line approver; verifies facts (dates, amount) | Reporting officer (e.g., Asst. Prof → HOD's designate) | Senior Resident → Unit Head |
| **L2** | Head of Department (HOD) | Departmental budget holder; verifies need | HOD — Mechanical Engineering | HOD — General Medicine |
| **L3** | Principal / HR Head | Institution-level; verifies policy compliance | Principal + HR Head (joint) | Medical Superintendent + HR Director |
| **L4 — Final** | Chairman / Secretary (optional, for high-impact) | Sign-off for budget > ₹X, or legal exposure | Chairman / Secretary (for amounts > ₹5 lakh) | Chairman (for amounts > ₹10 lakh) |

> **Shorthand:** In the CSV below, levels are written as `L1-RoleName`, `L2-RoleName`, etc. for compactness.

**Frappe HR mapping:**

| Concept | Frappe HR mechanism |
|---|---|
| L1 approver | `Employee.leave_approver` (per-employee) OR `Department.leave_approvers` (per-department child table) |
| L2 approver | `Department.leave_approvers[].approver` (priority after L1) |
| L3 approver | Workflow transition action (custom — set in Workflow DocType) |
| L4 approver | Workflow transition action (Chairman / Secretary) |
| Skip levels for low-impact docs | HR Settings → `leave_approver_mandatory_in_leave_application = 0` + custom workflow transitions |
| Amount-based routing | Custom DocType with `if amount > X: skip L2` rule, OR Python validation in workflow |

---

## 2. Document Type Catalog (10 types)

### 2.1 Leave Application

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee submits leave request (any of CL, SL, EL, ML, etc. from A6) |
| 2 | **L1 — Immediate Manager** | Reporting officer (e.g., Section Head, Senior Resident) |
| 3 | **L2 — HOD** | Head of Department |
| 4 | **L3 — Principal / HR** | Principal (academic) + HR Head (for policy compliance) |
| 5 | **L4 — Final (Chairman)** | NOT REQUIRED for leave |
| 6 | **Amount / day threshold for escalation** | > 5 consecutive days: skip to L3 |
| 7 | **SLA** | 24 hours per approver level |
| 8 | **Auto-approval** | None — leave always needs human review |

**Frappe HR setup:** Standard `Leave Application` workflow. L1 = `Employee.leave_approver`. L2 = `Department.leave_approvers` child table. L3 = `HR Manager` role. Skip L3 if `days_requested ≤ 2` AND `leave_type = CL`.

**Common client mistakes:**
- Routing all leave to HR first (bypasses manager — slows approval, breaks reporting-line authority)
- Forgetting to add Department-level approvers in `leave_approvers` child table (fallback fails silently)
- Allowing self-approval (violates `prevent_self_leave_approval` HR Setting; must be 1 for medical colleges)

### 2.2 On-Duty (OD) / Official Duty

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee submits OD request (conference, FDP, exam duty, university inspection) |
| 2 | **L1 — Immediate Manager** | Reporting officer |
| 3 | **L2 — HOD** | Head of Department |
| 4 | **L3 — Principal / HR** | Principal (for academic OD) or HR Head (for admin OD) |
| 5 | **L4 — Final (Chairman)** | NOT REQUIRED for OD |
| 6 | **Amount / day threshold for escalation** | > 3 days: requires Principal approval; > 7 days: requires Chairman |
| 7 | **SLA** | 48 hours per approver level |
| 8 | **Auto-approval** | None, but pre-approved annual OD calendar (e.g., FDPs in July) can be loaded as bulk |

**Frappe HR setup:** Custom DocType `On Duty Application` OR use `Leave Application` with `Leave Type = "On Duty"`. Add custom field `od_event_details` (link to event / conference) and `od_payable` (whether TA/DA is admissible). L3 = Principal for academic, HR Head for admin.

**Common client mistakes:**
- Conflating OD with leave (OD should NOT deduct from leave balance; the employee IS working)
- Missing the `od_payable` flag (TA/DA eligibility depends on whether it's external / internal)
- Not maintaining an OD register for audit (UGC / NAAC inspections ask for OD register)

### 2.3 Shift Change Request

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee (or scheduler) requests a shift swap / change |
| 2 | **L1 — Immediate Manager** | Shift in-charge / Nursing Supervisor (hospital) / Senior faculty member (college) |
| 3 | **L2 — HOD** | Head of Department |
| 4 | **L3 — Principal / HR** | NOT REQUIRED (unless shift change affects payroll) |
| 5 | **L4 — Final (Chairman)** | NOT REQUIRED |
| 6 | **Amount / day threshold for escalation** | > 3 consecutive days: L2 approval required |
| 7 | **SLA** | 12 hours per approver level (operational urgency) |
| 8 | **Auto-approval** | Yes, for one-off same-day swaps between two willing employees with matching shifts |

**Frappe HR setup:** `Shift Request` DocType (HRMS-native). L1 = `Employee.shift_request_approver` (custom field on Employee, similar to leave_approver). L2 = Department-level approver. Auto-approval rule: if `from_date = to_date` AND `both_employees_consent = 1`, skip workflow and create Shift Assignment directly.

**Common client mistakes:**
- Confusing Shift Request (one-off change) with Shift Schedule (recurring pattern)
- Forgetting to set `Employee.shift_request_approver` (leaves the workflow in limbo)
- Not auto-creating Shift Assignment on approval (HRMS does this if workflow is correctly configured)

### 2.4 Compensatory Off Request

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee requests to be granted Comp Off for extra work done (off-day, holiday, exam duty on Sunday) |
| 2 | **L1 — Immediate Manager** | Reporting officer (must verify the extra day was actually worked) |
| 3 | **L2 — HOD** | Head of Department (confirms with biometric / attendance data) |
| 4 | **L3 — HR** | HR Head (releases the Comp Off credit to leave balance) |
| 5 | **L4 — Final (Chairman)** | NOT REQUIRED |
| 6 | **Amount / day threshold for escalation** | None (always L1 → L2 → L3) |
| 7 | **SLA** | 48 hours |
| 8 | **Auto-approval** | None — biometric verification is required |

**Frappe HR setup:** Custom DocType `Compensatory Off Application` (NOT a Leave Application — it's a request to CREDIT a future leave, not to take one). Linked to `Attendance` (the original extra day) + `Leave Type = "Compensatory Off"` (the credit). Approval creates a Leave Allocation, not a Leave Application.

**Common client mistakes:**
- Using Leave Application (which DEDUCTS from balance) instead of a credit-side transaction
- Approving Comp Off without verifying the original work (encourages fake claims)
- Setting comp-off expiry > 90 days (encourages accumulation; defeats the "use it or lose it" intent)

### 2.5 Attendance Regularization

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee missed biometric punch OR has wrong punch (in-only / out-only) |
| 2 | **L1 — Immediate Manager** | Reporting officer (must verify presence via witness / CCTV / meeting log) |
| 3 | **L2 — HOD** | NOT REQUIRED (for single-day) |
| 4 | **L3 — HR** | HR (releases the regularization in attendance record) |
| 5 | **L4 — Final (Chairman)** | NOT REQUIRED |
| 6 | **Amount / day threshold for escalation** | > 3 days in a month: L2 approval required; > 5 days: Principal approval |
| 7 | **SLA** | 24 hours (operational) |
| 8 | **Auto-approval** | None — biometric discrepancy must be human-verified |

**Frappe HR setup:** HRMS `Attendance` DocType with `late_entry` / `early_out` flags. Custom DocType `Attendance Regularization Request` for missing punches. Linked to `Employee Checkin` (raw biometric data) and `Shift Type` (expected schedule). Approval updates the Attendance record.

**Common client mistakes:**
- Forgetting to set `HR Settings.send_attendance_notification = 1` (employees don't know they missed a punch)
- Allowing regularization of OUT-only punches without verifying the employee actually left (over-payment risk)
- Setting the regularization window > 7 days (encourages late reporting)

### 2.6 Tour Approval (Travel / TA-DA)

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee requests approval for an official tour (outstation travel with TA/DA eligibility) |
| 2 | **L1 — Immediate Manager** | Reporting officer (verifies purpose) |
| 3 | **L2 — HOD** | Head of Department (verifies departmental budget) |
| 4 | **L3 — Principal / HR** | Principal (for academic tours) or HR (for admin tours) |
| 5 | **L4 — Final (Chairman)** | REQUIRED if tour cost > ₹50,000 (or college-specific threshold) |
| 6 | **Amount / day threshold for escalation** | See L4 — varies per college |
| 7 | **SLA** | 72 hours per approver level |
| 8 | **Auto-approval** | None |

**Frappe HR setup:** Custom DocType `Tour Approval` with child table `Tour Itinerary` (city, date, purpose, estimated cost). Linked to `Travel Request` (HRMS) + `Expense Claim` (post-tour reimbursement). L4 routing is by amount, implemented via custom workflow transition `if total_estimated_cost > 50000: route to Chairman`.

**Common client mistakes:**
- Approving tour without budget verification (results in over-spend)
- Not requiring post-tour Expense Claim within 7 days (TA/DA fraud)
- Forgetting to set per-diem rates (DA varies by city class — use LTC + DA rules)

### 2.7 Loan / Salary Advance

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee requests salary advance (festive, medical emergency, education) |
| 2 | **L1 — Immediate Manager** | Reporting officer (verifies reason) |
| 3 | **L2 — HOD** | Head of Department (informational — does not block) |
| 4 | **L3 — HR + Finance** | HR (policy check) + Finance Officer (deduction schedule) |
| 5 | **L4 — Final (Principal)** | REQUIRED for loan amount > 1 month's gross salary |
| 6 | **Amount / day threshold for escalation** | ≤ ₹25,000: skip to L3; ₹25,001-1L: L3 only; > 1L: L3 + Principal |
| 7 | **SLA** | 5 working days |
| 8 | **Auto-approval** | None, but pre-approved festival advance in October can be a bulk auto-approval |

**Frappe HR setup:** `Employee Advance` DocType (HRMS-native). L1-L2 informational. L3 = `HR Manager` + `Accounts User` role (both must approve). L4 = Principal role for high-value advances. Repayment schedule auto-calculated via `Employee Advance` repayment table (typically 6-12 EMI deductions from salary).

**Common client mistakes:**
- Approving loan without a written repayment commitment (fraud risk)
- Setting EMI > 40% of net salary (over-commitment; defaults)
- Not tracking loan balance against future requests (employee stacks loans)
- Missing TCS / TDS impact on festival advance > ₹10,000 (tax implication post-2023)

### 2.8 Reimbursement (General — Travel, Internet, Books, etc.)

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee submits reimbursement claim with bills |
| 2 | **L1 — Immediate Manager** | Reporting officer (verifies bills are legitimate + within policy) |
| 3 | **L2 — HOD** | Head of Department (verifies departmental budget) |
| 4 | **L3 — HR + Finance** | HR (policy) + Finance Officer (payment) |
| 5 | **L4 — Final (Principal)** | REQUIRED for claim > ₹50,000 |
| 6 | **Amount / day threshold for escalation** | ≤ ₹5,000: skip to L3; ₹5,001-50K: L2+L3; > ₹50K: L2+L3+Principal |
| 7 | **SLA** | 7 working days (need time for bill verification) |
| 8 | **Auto-approval** | None, but recurring monthly reimbursements (e.g., internet allowance) can be auto-approved up to ₹3,000 |

**Frappe HR setup:** `Expense Claim` DocType (HRMS-native) with `Expense Claim Type` (Travel, Internet, Books, Phone, etc.). Custom workflow: L1 = reporting officer, L2 = HOD (skip if claim type = "Phone" and amount ≤ ₹2,000), L3 = HR Manager + Accounts User, L4 = Principal (workflow transition gated by `claim_amount > 50000`).

**Common client mistakes:**
- Approving without original bills (tax audit risk — bills are mandatory for TDS exemption)
- Missing the GSTIN on bills > ₹500 (input tax credit loss)
- Setting reimbursement policy caps without documenting them in the employee handbook
- Late submission window > 60 days (encourages fraud and accounting mess)

### 2.9 Medical Reimbursement

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee submits medical reimbursement claim (self or dependent) |
| 2 | **L1 — Reporting Officer** | Reporting officer (informational; doesn't block medical claims) |
| 3 | **L2 — HR** | HR Head (verifies policy — CGHS / ESI / corporate tie-up / self) |
| 4 | **L3 — Finance + Medical Officer** | Finance Officer (payment) + Medical Officer / Resident Medical Officer (verifies treatment was necessary) |
| 5 | **L4 — Final (Principal)** | REQUIRED for claim > ₹1,00,000 (or as per policy cap) |
| 6 | **Amount / day threshold for escalation** | ≤ ₹10,000: L2 only; ₹10,001-1L: L2+L3; > ₹1L: L2+L3+Principal |
| 7 | **SLA** | 10 working days (medical bills need careful verification) |
| 8 | **Auto-approval** | None, but pre-approved OPD cap of ₹2,000/month can be auto-approved |

**Frappe HR setup:** `Expense Claim` DocType with `Expense Claim Type = "Medical"` + custom field `treatment_type` (OPD / IPD / Day-care / Surgery / Diagnostic), `patient_name` (self / dependent), `hospital_name`, `is_cghs_esic` (Check). L2 = HR Manager. L3 = `Medical Officer` role + `Accounts User`. L4 = Principal (gated by amount).

**Critical:** If the college offers **ESIC** (Employee State Insurance for salary < ₹21,000/month) or **CGHS** (Central Government Health Scheme — rare for private colleges), the medical reimbursement must be processed AFTER the ESIC/CGHS claim, and the college reimburses only the residual. Build this into the workflow.

**Common client mistakes:**
- Approving without prescription + diagnostic reports (Income Tax scrutiny)
- Reimbursing non-allopathic treatment without prior approval (most policies exclude AYUSH)
- Missing the 90-day submission window (policy expiry)
- Not coordinating with ESIC (over-payment to employee)

### 2.10 Resignation Acceptance

| # | Attribute | Default value |
|---|-----------|---------------|
| 1 | **Trigger** | Employee submits resignation |
| 2 | **L1 — Immediate Manager** | Reporting officer (acknowledges; does not block) |
| 3 | **L2 — HOD** | Head of Department (acknowledges; does not block) |
| 4 | **L3 — HR + Principal** | HR (processes exit: notice period, handover, FnF) + Principal (final acceptance for teaching) |
| 5 | **L4 — Final (Chairman)** | REQUIRED for senior faculty (Professor, HOD level) — college-specific |
| 6 | **Amount / day threshold for escalation** | Notice period < 30 days: requires Chairman waiver |
| 7 | **SLA** | 30 days standard notice (employment contract override) |
| 8 | **Auto-approval** | None, but standard 90-day notice-period resignation can be auto-acknowledged |

**Frappe HR setup:** `Employee` DocType with `resignation_letter_date`, `relieving_date`, `reason_for_leaving` (custom). Custom workflow `Resignation Acceptance` with stages: Submitted → Acknowledged → Notice Period Served → FnF Processed → Status = Left. L1/L2 are auto-acknowledgement (system-driven). L3 = HR Manager + Principal. L4 = Chairman for senior staff.

**Common client mistakes:**
- Forgetting to set `relieving_date` (employee stays on rolls indefinitely)
- Not running FnF (Full and Final Settlement) calculation (PF, gratuity, leave encashment)
- Allowing resignation during probation without 15-day notice (policy violation)
- Missing the "no dues" workflow (library, IT assets, hostel — important for colleges)
- Releasing the experience letter / relieving letter before FnF cleared

---

## 3. Special Approval Edge Cases

| # | Edge case | Default behaviour | What to surface |
|---|---|---|---|
| 1 | **Approver is on leave** | Workflow auto-routes to L2 if L1 is on leave for > 3 days | Use HR Settings `prevent_self_leave_approval = 1` and define fallback approver in Department.leave_approvers child table |
| 2 | **Approver is the applicant** | System blocks self-approval | Set `prevent_self_approval = 1` in the workflow definition (mandatory for medical colleges per NMC) |
| 3 | **Applicant is Chairman / Principal** | Direct auto-approval | Set up "self-approval exception" or route to Board for Chairman resignations |
| 4 | **Cross-department approval needed** | Routes to both HODs | Use `multi-level workflow` with `parallel approval` configuration |
| 5 | **Applicant is on long leave (>30 days)** | Auto-route to L2 directly | L1 may not be available; skip-level routing |
| 6 | **Backdated application** | Flag for HR review | Date validation: `from_date >= today - 7 days`; else require L3 approval with reason |
| 7 | **Bulk approval (e.g., 50 leaves for a sports day)** | Bulk import via tool | Use Frappe HR's Data Import on `Leave Application` with `auto_approve = 1` flag (HR Manager only) |
| 8 | **Approval on a public holiday** | SLA pauses | Document: "SLA excludes Sundays + public holidays + declared holidays" |
| 9 | **Re-approval after rejection** | New application required | Don't allow edit-and-resubmit; force new workflow to preserve audit trail |
| 10 | **Withdrawal after partial approval** | Allowed; L3 must re-approve on re-submit | Reset workflow state on withdrawal |

---

## 4. CSV Schema (for Excel / Google Sheets import)

One row per document type, per institution. For multi-campus institutions, one set of rows per campus.

```csv
document_type,document_code,L1_role,L2_role,L3_role,L4_role,amount_threshold_L4,sla_hours_L1,sla_hours_L2,sla_hours_L3,sla_hours_L4,auto_approval_rule,frappe_workflow_name
"Leave Application","LEAVE","Reporting-Officer","HOD","Principal-and-HR-Head","None",0,24,24,24,0,"None","leave_application_workflow"
"On-Duty","OD","Reporting-Officer","HOD","Principal-academic-or-HR-Head-admin","None",0,48,48,48,0,"None if days<=1","on_duty_workflow"
"Shift Change","SHIFT","Shift-Incharge","HOD","None","None",0,12,12,0,0,"Same-day swap with both-consent","shift_request_workflow"
"Compensatory Off","COMP","Reporting-Officer","HOD","HR-Head","None",0,48,48,48,0,"None","compensatory_off_workflow"
"Attendance Regularization","ATTREG","Reporting-Officer","None","HR-Head","None",0,24,0,24,0,"None","attendance_regularization_workflow"
"Tour Approval","TOUR","Reporting-Officer","HOD","Principal-or-HR-Head","Chairman-if-amount>50000",50000,72,72,72,72,"None","tour_approval_workflow"
"Loan / Salary Advance","LOAN","Reporting-Officer","HOD-informational","HR-Head-and-Finance-Officer","Principal-if-amount>1L-GS",100000,120,0,120,120,"None","employee_advance_workflow"
"General Reimbursement","REIMB","Reporting-Officer","HOD","HR-Head-and-Finance-Officer","Principal-if-amount>50000",50000,168,168,168,168,"Recurring-monthly-cap-3000","expense_claim_workflow"
"Medical Reimbursement","MEDREIMB","Reporting-Officer-informational","HR-Head","Finance-Officer-and-Medical-Officer","Principal-if-amount>1L",100000,240,240,240,240,"OPD-cap-2000-per-month","medical_reimbursement_workflow"
"Resignation Acceptance","RESIGN","Reporting-Officer-auto","HOD-auto","HR-Head-and-Principal","Chairman-if-senior-faculty",0,720,720,720,720,"90-day-notice-auto-acknowledge","resignation_acceptance_workflow"
```

**3-4 sample institutions (one row per institution — full matrix per institution):**

```csv
institution_name,institution_type,total_doc_types,L1_chain,L2_chain,L3_chain,L4_chain,common_remarks
"XYZ Engineering College (Hyderabad)","Engineering College",10,"Reporting Officer always","HOD of department","Principal + HR Head","Chairman for tour > ₹50K; loan > ₹1L; medical > ₹1L; senior faculty resign","Standard 4-level; no hospital chain; 5-day SLA on average"
"ABC Medical College and Hospital (Chennai)","Combined (Medical + Paramedical)",10,"Senior Resident / Section Head / Lab Incharge","HOD of clinical department","Medical Superintendent + HR Director","Chairman for any amount > ₹5L or senior faculty","NMC self-approval ban; clinical workflow with RMO verification on medical claims"
"Delhi University — Faculty of Science (Delhi)","University (State)",10,"Supervisor / Section Head","Department Chair","Dean + Registrar","Vice-Chancellor for amounts > ₹2L; senior faculty resign","UGC governance; VC approval for all academic senior staff resign"
"Lakeside Polytechnic (Coimbatore)","Polytechnic",10,"Section Head","HOD","Principal + Admin Officer","Chairman for tour > ₹25K; loan > ₹50K","Smaller institution; flat 3-level chain with L4 only for ₹ thresholds"
```

**Validation column (notes for the HR Lead filling this CSV):**

| Column | Validation rule |
|---|---|
| `document_type` | One of the 10 in §2 (or a new 11th if the client has a custom document) |
| `document_code` | 4-10 chars, all uppercase, unique within the file |
| `L1_role` / `L2_role` / `L3_role` / `L4_role` | Free text; describe the role, not the person. Use `None` if not required |
| `amount_threshold_L4` | Numeric ≥ 0; triggers L4 routing when exceeded |
| `sla_hours_L1` / etc. | Numeric; 0 if level not required |
| `auto_approval_rule` | Free text; document any automatic approval condition |
| `frappe_workflow_name` | Must match the Frappe HR Workflow DocType name (created during Phase 0 / 1) |

---

## 5. Sign-off

By signing below, the signatory confirms that the approval hierarchy described in this form reflects the institution's current delegation of authority, that the monetary thresholds are authorised by the Board / Chairman, and that the institution authorises College HR Foundation to encode these workflows in Frappe HR.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| HR Lead (form owner) | | | |
| Principal / Director | | | |
| Finance Officer (confirms monetary thresholds) | | | |
| Chairman / Secretary (optional, for high-impact workflows) | | | |

**Form version:** v1.0 (2026-10-15)
**Status:** ✅ Ready for prospect use
**Owner:** Venkat Narasimha, College HR Foundation

---

## Related

- [[A1-org-profile]] — Provides decision-maker names that map to these role-based approvers
- [[A6-leave-policy]] — Defines which leave types trigger Section 2.1's Leave Application workflow
- [[B1-discovery-questionnaire]] — Phase 2 §4 walks through this form live with the client
- `knowledge/hr_payroll.md` — Reference on Workflow / Employee / Department DocTypes in Frappe HR

---

## Changelog

| Date | Changes |
|------|---------|
| 2026-10-15 | Initial v1.0 — 10 document types with 4-level approval chain, SLA per level, auto-approval rules, 10 edge cases, 4 sample institutions (engineering, medical, university, polytechnic) |
