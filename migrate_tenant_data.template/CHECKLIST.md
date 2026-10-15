# Pre-onboarding checklist

Before you clone `migrate_tenant_data.template/` for a new prospect,
confirm each item below. This is the 5-minute gate that prevents a
3-day re-migration later.

## Must-have (blocks the migration)

- [ ] **Client has signed the SOW / engagement letter.** Without this,
      the prospect's data folder is hypothetical and you'll re-rename
      it twice. *Where to look:* the SOW itself, the CRM, or
      `decisions/ARCHITECTURE-DECISIONS-QA.md` Q4 for the named pilot.

- [ ] **Client has filled `templates/A1-org-profile.md`.** This drives
      `company.csv`, `department.csv`, `designation.csv`, and the
      `company_name` / `company_abbr` fields in `tenant_config.json`.
      *If missing:* ask the prospect's HR head to complete A1; do not
      invent the org chart from the website.

- [ ] **Client has filled `templates/A6-leave-policy.md`.** This drives
      `leave_type.csv`, `leave_policy.csv`, `leave_policy_detail.csv`,
      and the `leave_type_defaults` block in `tenant_config.json`.
      *If missing:* reuse the India-statutory defaults already in the
      template (PL/CL/SL/Earned/Maternity/Paternity) and flag A6 as a
      Phase 2 follow-up.

- [ ] **Client has filled `templates/A7-approval-matrix.md`.** This
      drives `approver_user` in `tenant_config.json` and the
      `reports_to` / `leave_approver` / `expense_approver` columns in
      `employee.csv`. *If missing:* leave `approver_user` as
      `"Administrator"` for the first dry-run and replace with the
      real HR head's Frappe user ID before the live migration.

- [ ] **Client has confirmed their fiscal-year start month and
      timezone.** These two values in `tenant_config.json` flow into
      Holiday List date ranges and every timestamp in the system.
      *Where to look:* the client's HR manual or finance team. India
      default is April-start, Asia/Kolkata. Override per prospect.

- [ ] **`decisions/ARCHITECTURE-DECISIONS-QA.md` Q1, Q2, Q3, Q4 are
      all answered or explicitly deferred.** Q1 (tenancy), Q2 (app
      name), Q3 (domain) are pre-baked defaults; Q4 (pilot contact) is
      `"TODO"` until Venkat names the pilot. *If Q4 is still TODO and
      this is the first prospect:* block the migration and ping Venkat.

## Nice-to-have (improves the first migration but not blocking)

- [ ] **A test Frappe HR site exists for the prospect's domain**
      (e.g. `stmarys.chronova.in` is reachable, has a Frappe login
      page, and you have admin credentials). *Where to look:* the
      platform's site-provisioning script or your hosting dashboard.

- [ ] **A backup of the empty site exists.** So a misconfigured
      migration can be wiped + retried in <5 minutes rather than
      hand-cleaned. *Where to look:* `bench --site <site> backup
      --with-files` output.

- [ ] **Biometric or attendance-device integration scope is
      confirmed.** If the client has a biometric, you'll need
      `templates/A4-attendance-integration.md` filled too (out of
      scope for `migrate_tenant_data.py` itself but needed before
      go-live). *If unconfirmed:* note it in the engagement
      timeline as a Phase 5 task.

- [ ] **A comms plan exists for the welcome email + first login
      credentials.** The platform owner needs the prospect's primary
      HR contact's email before the first user invite goes out.

## When all boxes are checked

You're ready to run **Step 1** of `README.md` (`cp -r` the template).
The whole onboarding flow from clone to live-run takes about 2-4
hours for a typical 50-250-employee college.
