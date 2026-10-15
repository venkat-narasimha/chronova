# A1 — Organization Profile Intake

---

## What This Is

This is the **first intake form** Chronova sends to every prospect **after the discovery meeting, before signing the Statement of Work**. It captures the institutional facts we need to provision a Frappe HR instance that matches the institution's structure on Day 1.

The form has two halves: (a) institutional / academic profile (what kind of college you are, who regulates you, what you teach), and (b) HR / operational profile (how many people you employ, how you run payroll, who your decision-makers are, when you want to go live). Every field maps to a downstream configuration decision in Frappe HR.

## Who Fills It

The **HR Lead or HR Manager** of the prospect institution is the primary owner. They complete the form, but they should consult three colleagues:

- **Principal / Director** — for the academic profile (programmes, accreditations, year of establishment)
- **Finance Officer / CFO** — for payroll ownership, current HR software spend, banking
- **IT Head / Systems Manager** — for the IT landscape, biometric devices, data export capability

In a smaller institution (under 100 employees) the **HR Lead** may complete all sections solo. The principal signs off the bottom.

## When To Use It

Use this form at **one of three moments**:

| Moment | When | Why |
|---|---|---|
| **Pre-discovery** | Sent 48 hours before the first meeting | Lets the consultant walk in already knowing the org chart and accreditations |
| **At discovery** | Opened live during the meeting (Phase 2 of B1) | Captures answers in real time while the consultant is asking the questions |
| **Post-discovery** | Sent 24 hours after the meeting as a follow-up | Confirms the answers captured and fills any gaps discovered during technical/commercial phases |

The form is the **canonical source of truth** for the Statement of Work. The SOW cannot be drafted until this form is fully completed and signed at the bottom.

---

## 1. Institutional Profile

### 1.1 Identity

| # | Field | Type | Required | Example | Validation / Notes |
|---|-------|------|:--------:|---------|---------------------|
| 1.1.1 | **Legal name of the institution** | Text | ✅ | XYZ College of Engineering and Technology (Private) Limited | Match the name on PAN / GST certificate exactly |
| 1.1.2 | **Display / brand name** | Text | ✅ | XYZ Engineering College | What you call yourselves on the website / letterhead |
| 1.1.3 | **Institution type** | Dropdown | ✅ | Engineering College | Options: Medical College, Engineering College, Combined (Medical + Engineering / Paramedical), University (Deemed / State / Private / Central), Polytechnic, Nursing College, Allied Health Sciences College, Other |
| 1.1.4 | **Year of establishment** | Number (YYYY) | ✅ | 2008 | Four-digit year; used for accreditation eligibility checks |
| 1.1.5 | **Registration / Trust name** | Text | ✅ | XYZ Educational Trust | The parent society / trust / company that owns the college |
| 1.1.6 | **PAN of institution** | Text | ✅ | AABCX1234E | 10-character alphanumeric; required for TDS filings |
| 1.1.7 | **GSTIN** | Text | ⚪ | 27AABCX1234E1Z5 | 15-character; required if turnover > ₹20 lakh (services) or ₹40 lakh (goods) |

### 1.2 Location & Branches

| # | Field | Type | Required | Example | Validation / Notes |
|---|-------|------|:--------:|---------|---------------------|
| 1.2.1 | **Registered office address** | Multi-line text | ✅ | Plot 14, Sector 7, MIDC Industrial Area, Hyderabad — 500081, Telangana | Full postal address with PIN code |
| 1.2.2 | **Number of campuses / branches** | Number | ✅ | 1 | If > 1, fill 1.2.3 per campus |
| 1.2.3 | **Campus list** | Repeating block | ⚪ | Main Campus (Hyderabad); Second Campus (Warangal) | Name + city + state + PIN per campus |
| 1.2.4 | **State(s) of operation** | Multi-select | ✅ | Telangana, Andhra Pradesh | Each state may have different Shops & Establishments Act rules |
| 1.2.5 | **Website** | URL | ⚪ | https://www.xyz.edu.in | Public-facing website |
| 1.2.6 | **Primary email** | Email | ✅ | info@xyz.edu.in | Public-facing; bounces here should go to the HR lead |

### 1.3 Accreditations & Regulatory Bodies

| # | Field | Type | Required | Example | Notes |
|---|-------|------|:--------:|---------|-------|
| 1.3.1 | **Regulatory approvals held** | Multi-select | ✅ | AICTE, UGC, NBA | Choose all that apply: UGC, AICTE, NMC (formerly MCI), DCI (Dental), INC (Nursing), PCI (Pharmacy), Bar Council, NAAC, NBA, NIRF, ISO, Other |
| 1.3.2 | **University affiliation** | Text | ⚪ | Jawaharlal Nehru Technological University, Hyderabad | If affiliated (not autonomous / not deemed) |
| 1.3.3 | **NAAC grade** | Dropdown | ⚪ | A | A++ / A+ / A / B++ / B+ / B / C / Not accredited |
| 1.3.4 | **NIRF rank (latest year)** | Text | ⚪ | 87 (Engineering, 2025) | "Band 151-200" if ranked in band |
| 1.3.5 | **Accreditation valid until** | Date | ⚪ | 2027-03-31 | When the next renewal cycle is due |
| 1.3.6 | **Annual student intake (total across all programmes)** | Number | ✅ | 720 | Sum of all approved seats |
| 1.3.7 | **Total active student strength** | Number | ✅ | 2,640 | Current roll across all years and programmes |
| 1.3.8 | **Active programmes / departments** | Repeating text | ✅ | CSE, ECE, EEE, MECH, CIVIL, MBA | One per line; matches your Department master in Frappe HR |

---

## 2. Human Resources Profile

### 2.1 Employee Headcount (as of today)

| # | Category | Count | Notes |
|---|----------|------:|-------|
| 2.1.1 | Teaching staff (full-time) | 142 | Professors, Associate Profs, Assistant Profs, Tutors — full-time only |
| 2.1.2 | Teaching staff (visiting / part-time / guest) | 28 | Adjunct faculty, visiting faculty, guest lecturers |
| 2.1.3 | Non-teaching academic (lab assistants, librarians) | 35 | Lab techs, library staff, language lab staff |
| 2.1.4 | Medical / clinical staff (medical colleges only) | 78 | Residents, Tutors (clinical), Medical Officers |
| 2.1.5 | Paramedical / allied health (medical colleges only) | 22 | Physiotherapists, OT techs, pharmacists in hospital |
| 2.1.6 | Administrative / office staff | 19 | Office superintendent, accountants, clerks, receptionists |
| 2.1.7 | Housekeeping / security / maintenance / drivers | 41 | Outsourced + in-house mixed; indicate split in 2.1.10 |
| 2.1.8 | **TOTAL active employees** | **365** | Sum of 2.1.1 to 2.1.7 |
| 2.1.9 | **Employees on long-term leave (≥30 days)** | 7 | Maternity, sabbatical, medical — still on payroll |
| 2.1.10 | **Outsourced headcount (third-party payroll)** | 68 | Housekeeping, security, transport — paid by vendor but on campus |
| 2.1.11 | **Contract / part-time headcount** | 14 | Fixed-term contracts, retainers, consultants |

### 2.2 Compensation & Payroll

| # | Field | Type | Required | Example | Notes |
|---|-------|------|:--------:|---------|-------|
| 2.2.1 | **Payroll handled by** | Dropdown | ✅ | In-house (single HR + accounts team) | In-house / Outsourced (third-party payroll vendor) / Hybrid (in-house for permanent, vendor for contract) |
| 2.2.2 | **Payroll vendor name** (if outsourced) | Text | ⚪ | ADP India / Ramco / Custom Excel | Vendor name + contract expiry |
| 2.2.3 | **Payroll cycle** | Dropdown | ✅ | Monthly, last working day | Monthly / Bi-monthly / Weekly / Custom date |
| 2.2.4 | **Average monthly payroll (gross, INR)** | Currency | ✅ | ₹1,42,00,000 | Used to size infrastructure; INR only |
| 2.2.5 | **Statutory deductions handled** | Multi-select | ✅ | PF, ESI, PT, TDS, LWF | Provident Fund, Employee State Insurance, Professional Tax, TDS, Labour Welfare Fund |
| 2.2.6 | **Bank for salary disbursement** | Text | ✅ | HDFC Bank — Jubilee Hills branch | Primary bank; can be multiple (list primary first) |
| 2.2.7 | **Payroll sign-off authority** | Text | ✅ | Mr. Suresh Rao, CFO | Person who authorises the final disbursement |

### 2.3 Current HR Software & IT Landscape

| # | Field | Type | Required | Example | Notes |
|---|-------|------|:--------:|---------|-------|
| 2.3.1 | **Current HR / payroll software** | Dropdown | ✅ | Tally + Excel | Options: SAP, Oracle HCM, Darwinbox, Keka, greytHR, ADP, Tally + Excel, Custom (VBA / Access), Paper-based, None |
| 2.3.2 | **Software version (if applicable)** | Text | ⚪ | Tally Prime 3.0 | Helps us plan data extraction |
| 2.3.3 | **Years on current software** | Number | ✅ | 4 | If < 2 years, expect migration fatigue — flag in discovery |
| 2.3.4 | **Biometric / attendance device in use** | Text | ⚪ | eSSL X990 (fingerprint + RFID) — 6 devices across 3 campuses | Brand + model + count + campus coverage |
| 2.3.5 | **Biometric data export format** | Dropdown | ⚪ | Excel / CSV (manual) | Direct API / Excel-CSV / SFTP / None / Manual paper register |
| 2.3.6 | **IT team size supporting HR systems** | Number | ✅ | 2 | If 0, expect capacity gap — flag in discovery |
| 2.3.7 | **Email provider** | Dropdown | ✅ | Google Workspace | Google Workspace / Microsoft 365 / Zoho Mail / On-premise Exchange / Custom SMTP |
| 2.3.8 | **Active Directory / SSO** | Dropdown | ✅ | None (future plan) | Active Directory / Google SSO / Microsoft Entra ID / None / Planned |
| 2.3.9 | **Internet uptime (last 30 days)** | Dropdown | ✅ | > 99% | > 99% / 95-99% / 90-95% / < 90% — affects hosted vs on-premise decision |

### 2.4 Decision-Makers (DM) & Stakeholders

Fill one row per role. The **primary decision-maker** for the SaaS purchase must be the **Chairman / Secretary / Correspondent** of the trust (not the Principal).

| # | Role | Name | Mobile | Email | Authority for what | Decision-maker? |
|---|------|------|--------|-------|---------------------|:---:|
| 2.4.1 | **Chairman / Secretary / Correspondent** | Dr. K. R. Reddy | +91 98XXX XXXXX | chairman@xyz.edu.in | Budget sign-off, go/no-go | ✅ |
| 2.4.2 | **Principal / Director** | Dr. Anjali Verma | +91 98XXX XXXXX | principal@xyz.edu.in | Academic policy, final HR sign-off | ⚪ |
| 2.4.3 | **Vice-Principal** | Prof. S. Murthy | +91 98XXX XXXXX | vp@xyz.edu.in | Academic operations | ⚪ |
| 2.4.4 | **HR Head / HR Manager** | Ms. Lakshmi Iyer | +91 98XXX XXXXX | hr@xyz.edu.in | Day-to-day HR, this project | ⚪ |
| 2.4.5 | **CFO / Finance Officer** | Mr. Suresh Rao | +91 98XXX XXXXX | finance@xyz.edu.in | Payroll, vendor payments | ⚪ |
| 2.4.6 | **IT Head / Systems Manager** | Mr. Prakash K | +91 98XXX XXXXX | it@xyz.edu.in | Infrastructure, integration | ⚪ |
| 2.4.7 | **Accounts Officer (Payroll)** | Ms. Sneha P | +91 98XXX XXXXX | accounts@xyz.edu.in | Payroll execution | ⚪ |
| 2.4.8 | **Legal / Compliance Officer** | Mr. R. Krishnan | +91 98XXX XXXXX | legal@xyz.edu.in | Statutory compliance, audits | ⚪ |

### 2.5 Go-Live & Project Constraints

| # | Field | Type | Required | Example | Notes |
|---|-------|------|:--------:|---------|-------|
| 2.5.1 | **Target go-live date** | Date | ✅ | 2027-04-01 | Must be a month-end (last working day preferred for payroll cutover) |
| 2.5.2 | **Why this date?** | Text | ✅ | "Q1 audit + new financial year start" | Admission cycle / academic year / financial year / audit / board review |
| 2.5.3 | **Hard deadline (board / regulator)?** | Date | ⚪ | 2027-06-30 | If the date in 2.5.1 slips, when is the absolute no-go? |
| 2.5.4 | **Annual leave cycle start month** | Dropdown | ✅ | April (financial year) | Indian FY = Apr-Mar; some colleges use calendar year; some use academic year (Jun-Jul) |
| 2.5.5 | **Academic year start month** | Dropdown | ✅ | July | When new academic session starts |
| 2.5.6 | **Active leave blocks during cutover** | Text | ⚪ | "May 1-15 (summer break); Dec 20-31 (winter)" | Periods when staff are off; useful for migration windows |
| 2.5.7 | **Hard constraints / non-negotiables** | Multi-line text | ⚪ | "PF must continue from Tally; medical OPD staff on different shift policy" | Anything we MUST preserve in the new system |
| 2.5.8 | **Current pain points (rank 1-5)** | Text | ✅ | 1. Manual attendance reconciliation 2. No leave balance visibility for staff 3. TDS miscalculations in Excel | Top 3-5 specific issues we must solve |

---

## 3. CSV Schema (for Excel / Google Sheets import)

Copy the headers below into row 1 of a new Google Sheet or Excel file. Add one row per institution (in case of multi-campus groups, one row per legal entity). All cells are free-text unless marked.

```csv
legal_name,display_name,institution_type,year_established,trust_name,pan,gstin,registered_address,num_campuses,states_of_operation,website,primary_email,regulatory_approvals,university_affiliation,naac_grade,nirf_rank,accreditation_valid_until,annual_student_intake,total_student_strength,active_programmes,teaching_full_time,teaching_visiting,non_teaching_academic,medical_clinical,paramedical,admin_office,housekeeping_security,total_employees,long_term_leave,outsourced_headcount,contract_part_time,payroll_handled_by,payroll_vendor,payroll_cycle,avg_monthly_gross_payroll_inr,statutory_deductions,bank_salary_disbursement,payroll_signoff_authority,current_hr_software,software_version,years_on_current_software,biometric_device,biometric_export_format,it_team_size,email_provider,sso_provider,internet_uptime,chairman_name,chairman_mobile,chairman_email,principal_name,principal_mobile,principal_email,vp_name,vp_mobile,vp_email,hr_head_name,hr_head_mobile,hr_head_email,cfo_name,cfo_mobile,cfo_email,it_head_name,it_head_mobile,it_head_email,target_go_live,go_live_reason,hard_deadline,leave_cycle_start_month,academic_year_start_month,active_leave_blocks,hard_constraints,top_5_pain_points,form_completed_by,form_completion_date
"XYZ College of Engineering and Technology Pvt Ltd","XYZ Engineering College","Engineering College",2008,"XYZ Educational Trust","AABCX1234E","27AABCX1234E1Z5","Plot 14 Sector 7 MIDC Hyderabad 500081 Telangana",1,"Telangana","https://www.xyz.edu.in","info@xyz.edu.in","AICTE|UGC|NBA","Jawaharlal Nehru Technological University Hyderabad","A","87 (Engineering 2025)","2027-03-31",720,2640,"CSE|ECE|EEE|MECH|CIVIL|MBA",142,28,35,0,0,19,41,265,7,68,14,"In-house","N/A","Monthly last working day",14200000,"PF|ESI|PT|TDS|LWF","HDFC Bank Jubilee Hills","Suresh Rao CFO","Tally + Excel","Tally Prime 3.0",4,"eSSL X990 fingerprint RFID x6 across 3 campuses","Excel CSV manual",2,"Google Workspace","None future plan",">99%","Dr K R Reddy","+919800000001","chairman@xyz.edu.in","Dr Anjali Verma","+919800000002","principal@xyz.edu.in","Prof S Murthy","+919800000003","vp@xyz.edu.in","Ms Lakshmi Iyer","+919800000004","hr@xyz.edu.in","Mr Suresh Rao","+919800000005","finance@xyz.edu.in","Mr Prakash K","+919800000006","it@xyz.edu.in","2027-04-01","Q1 audit new financial year","2027-06-30","April","July","May 1-15 summer break Dec 20-31 winter","PF must continue from Tally","1 Manual attendance reconciliation 2 No leave balance visibility 3 TDS miscalculations 4 No mobile access 5 Slow approvals","Ms Lakshmi Iyer HR Manager","2026-11-15"
"ABC Medical College and Hospital","ABC Medical College","Combined (Medical + Paramedical)",1998,"ABC Health and Education Trust","AABCA5678F","33AABCA5678F1Z9","42 GST Road Chennai 600016 Tamil Nadu",2,"Tamil Nadu|Karnataka","https://www.abcmedical.edu.in","admissions@abcmedical.edu.in","NMC|UGC|NAAC|NIRF","The Tamil Nadu Dr MGR Medical University","A++","52 (Medical 2025)","2028-12-31",650,2380,"Anatomy|Physiology|Biochemistry|Pathology|Microbiology|Pharmacology|Community Medicine|General Medicine|General Surgery|OBG|Pediatrics|Ortho|Anaesthesia|Radiology|Dermatology|Psychiatry|ENT|Ophthalmology|Nursing|Physiotherapy",118,12,28,180,95,32,38,503,12,120,18,"Hybrid","ADP India contract ends 2027-03","Monthly 28th",38500000,"PF|ESI|PT|TDS|LWF","ICICI Bank Anna Nagar","Mr Vijay Anand Director Finance","Custom in-house Access DB","Custom VBA Access 2016",7,"Mantra MFS100 fingerprint x12 + RFID x8","Excel CSV weekly SFTP",3,"Microsoft 365","Microsoft Entra ID (Azure AD)",">99%","Dr M K Balan","+919800000010","chairman@abcmedical.edu.in","Dr R Sridhar","+919800000011","principal@abcmedical.edu.in","Dr P Lakshmi","+919800000012","vp@abcmedical.edu.in","Mr Karthik R HR Director","+919800000013","hr@abcmedical.edu.in","Mr Vijay Anand","+919800000014","finance@abcmedical.edu.in","Ms Deepa S","+919800000015","it@abcmedical.edu.in","2027-07-01","New academic year NMC inspection","2027-09-30","January","August","Dec 25 Jan 5 Pongal Christmas","Hospital 24x7 shifts NMC compliance","1 Complex shift rosters 2 Statutory deadline tracking 3 Medical certificate management 4 Resident duty hours NMC cap 5 Paper-based attendance for nurses","Mr Karthik R HR Director","2026-11-18"
```

**Validation column (notes for the HR Lead filling this CSV):**

| Column | Validation rule |
|---|---|
| `legal_name` | Must match PAN card exactly (case-sensitive) |
| `institution_type` | One of the 8 values listed in 1.1.3 — no free text |
| `year_established` | 4-digit year between 1900 and current year |
| `pan` | 10 chars, regex `^[A-Z]{5}[0-9]{4}[A-Z]$` |
| `gstin` | 15 chars, regex `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z][Z][0-9A-Z]$` |
| `regulatory_approvals` | Pipe-separated list from 1.3.1; no spaces around pipes |
| `payroll_handled_by` | One of: `In-house` / `Outsourced` / `Hybrid` |
| `payroll_cycle` | Free text; we will normalise in Frappe HR |
| `avg_monthly_gross_payroll_inr` | Numeric, no commas, no rupee symbol |
| `target_go_live` | ISO date `YYYY-MM-DD`; preferably last working day of month |
| All phone numbers | `+91XXXXXXXXXX` format with country code |
| `form_completed_by` + `form_completion_date` | Last column — must match the sign-off below |

---

## 4. What Happens After You Submit

| Step | Day | What we do | What you do |
|---|:---:|------------|-------------|
| 1 | Day 0 | Receive completed A1 | Sign at the bottom |
| 2 | Day +1 | Validate the data, flag any gaps | Answer clarifying questions |
| 3 | Day +3 | Send back the populated A1 with our annotations | Review and confirm |
| 4 | Day +5 | Convert to Frappe HR master data templates (Company, Department, Designation, Employee Grade, Holiday List) | Validate our mapping |
| 5 | Day +7 | Share the Statement of Work referencing this A1 | Negotiate / sign SOW |
| 6 | Day +14 | Kick off Phase 0 (Environment Setup) | Nominate project coordinator |

---

## 5. Sign-off

By signing below, the signatory confirms that the information provided in this form is accurate to the best of their knowledge, and authorises Chronova to use this information for the purpose of drafting a Statement of Work and provisioning a Frappe HR instance.

| Role | Name | Signature | Date |
|------|------|-----------|------|
| HR Lead (form owner) | | | |
| Principal / Director | | | |
| CFO / Finance Officer | | | |
| Chairman / Secretary (optional, if budget pre-approved) | | | |


---

## Related

- [[A6-leave-policy]] — Leave policy intake (sent in parallel)
- [[A7-approval-matrix]] — Approval matrix intake (sent in parallel)
- [[B1-discovery-questionnaire]] — Internal script Venkat uses to fill this form
- [[audit-client-templates-2026-09-21]] — Background audit of Haritha Hospitals templates this builds on

---

## Changelog

| Date | Changes |
|------|---------|
| 2026-10-15 | Initial v1.0 — 12 institutional fields, 11 employee categories, 8 stakeholder roles, full CSV schema with 2 sample institutions (engineering + medical) |
