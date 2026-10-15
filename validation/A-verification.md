# A — Verification: 3 Default Decisions

**Date:** 2026-10-15 · **Reviewer:** Agent 4 · **Verdict:** ✅ All 3 defaults applied — **no B1 patch required**

Confirms the 3 default decisions Agent 1 selected (and Venkat did not override) are correctly captured in the deliverables. For Venkat + Agent 1.

---

## D1 — Scoring Rubric Thresholds
**Default:** 5-11 walk · 12-17 nurture · 18-25 prioritise
**Source:** `playbooks/B1-discovery-questionnaire.md` §6
**Status:** ✅ **APPLIED** — exact thresholds present.

> **Scoring cheat sheet:**
>
> | Total score | Action |
> |---|---|
> | 5-11 | Politely decline. Send a "not the right fit at this time" email. Revisit in 6 months. |
> | 12-17 | Nurture. Send a 2nd-meeting proposal within 2 weeks. Offer a discovery fee engagement to qualify. |
> | 18-25 | Prioritise. Send a draft SOW within 5 working days. Block 2 weeks of consultant time for Phase 0. |

(Section §6 also opens: *"Score < 12 = walk away; 12-17 = nurture; > 17 = prioritise"* — consistent.)

---

## D2 — Special Leave: 1 Leave Type + custom field
**Default:** 1 Leave Type `"Special Leave"` with custom field `special_leave_category` (8 sub-categories)
**Source:** `templates/A6-leave-policy.md` §1.8
**Status:** ✅ **APPLIED** — approach is documented.

> *These are typically a **single Leave Type** with **sub-categories** defined in a custom field. Indian labour law does not require these, but they are standard in college HR policies.*

> **Sub-categories** (custom field `special_leave_category`):
>
> | Sub-category | Days granted | Proof required |
> |---|:---:|---|
> | Bereavement (immediate family) | 7 | Death certificate |
> | Bereavement (extended family) | 3 | Death certificate |
> | Marriage (self) | 5 | Wedding invitation |
> | Paternity (within 6 months of birth) | 7-15 | Birth certificate |
> | Adoption | 12 weeks | Adoption order |
> | Study leave (PhD / higher study) | Up to 365 | Admission letter + principal recommendation |
> | Jury / civic duty | As required | Court summons |
> | Sports / cultural representation | As required | Selection letter from association |

> **Frappe HR mapping:** `Leave Type = "Special Leave"`, `is_special_leave = 1` (custom), `is_paid = 1`, `allow_negative = 0`, custom field `special_leave_category` (Select with the 8 sub-categories above).

---

## D3 — Follow-up Email SLA: 24 hours
**Default:** Send the post-meeting follow-up email within 24 hours of the meeting
**Source:** `playbooks/B1-discovery-questionnaire.md` §9
**Status:** ✅ **APPLIED** — SLA is in the section title and the sign-off table.

> **9. Follow-Up Email Template (send within 24 hours)**

The 24-hour SLA is captured in the **section header** `(send within 24 hours)` and the consultant's sign-off requires recording the date the email was sent.

**Minor observation (not a blocker):** the SLA is in the section title, not in the email body itself. For internal use this is fine. If Venkat wants the SLA visible to the prospect, a one-line addition in the email body would do it — but that's polish, not a missing default.

---

## Summary

| ID | Decision | Default | Status |
|---|---|---|:---:|
| D1 | Scoring rubric thresholds | 5-11 / 12-17 / 18-25 | ✅ applied |
| D2 | Special Leave approach | 1 Leave Type + `special_leave_category` | ✅ applied |
| D3 | Follow-up email SLA | 24 hours | ✅ applied |

**Net result:** Zero gaps. `A-patch-B1.md` is **NOT** created. Venkat can move to first prospect meeting with the current B1.

---

*See also: `B-spot-check.md` (A6/A7 review); `C-review-packet.md` (architecture working session).*
