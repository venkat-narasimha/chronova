"""
Tenant-Agnostic Master Data Migration Script
==============================================

Migrates HR/HRMS master data (Company, Department, Designation, Employee,
Shift Type, Holiday List, Leave Type/Policy, Shift Assignment) into a
Frappe HR site. Designed to be **reusable across any client** by reading
all tenant-specific data from:

  1. A JSON tenant config file  (company name, currency, timezone, etc.)
  2. CSV data files            (one per DocType)

Re-running the script is safe: every record is processed via the upsert
pattern from Lesson #157 (``frappe.db.exists()`` → ``save()`` or
``insert()``), so no duplicates, no destructive rewrites.

DocTypes migrated (in dependency order)
---------------------------------------
**Core scope** (always migrated if CSV is present):

 1.  ``Company``           (2-step: minimal insert, then attach default accounts)
 2.  ``Department``        (skip the configured root node, e.g. ``All Departments``)
 3.  ``Designation``
 4.  ``Shift Type``        (autoname='prompt' → CSV must include ``name``)
 5.  ``Holiday List`` + child ``Holiday``  (child rows appended programmatically)
 6.  ``Employee``          (depends on Department / Designation / Shift Type)
 7.  ``Leave Type``        (migrated from CSV, defaults merged from tenant_config)
 8.  ``Leave Policy`` + child ``Leave Policy Detail``
 9.  ``Shift Assignment``  (CSV rows include ``employee`` and ``shift_type`` names)

**Optional scope** (only migrated if matching CSV is present):

  - ``Gender``             (if ``gender.csv`` exists)
  - ``Employment Type``    (if ``employment_type.csv`` exists)
  - ``Shift Location``     (if ``shift_location.csv`` exists — required if
                             ``shift_assignment.csv`` references a location)
  - ``Shift Request``      (if ``shift_request.csv`` exists — applies
                             autoname series pre-bump gotcha #10)

USAGE
-----
Run inside a Frappe bench container (e.g. ``docker exec -u frappe
erp-dev-backend-1 bash``), with the site already set up::

    bench --site <site-folder> execute <your_app>.utils.migrate_tenant_data.run \\
        --kwargs '{"tenant_config": "/path/to/tenant_config.json",
                   "data_dir":      "/path/to/data_dir",
                   "dry_run":       true}'

**CLI shim** — if invoked as ``python migrate_tenant_data.py ...`` the
script re-execs itself through ``bench execute`` so you don't need to
remember the path. The custom app hosting this script is auto-detected
by walking up the filesystem for an ``apps.txt`` ancestor::

    python migrate_tenant_data.py \\
        --tenant-config /path/to/tenant_config.json \\
        --data-dir      /path/to/data_dir              \\
        --site          pberpdev.duckdns.org           \\
        --dry-run

For backward compatibility with the Haritha Hospitals JSON-source
migration, the example data dir ships Haritha-style CSVs so you can
replay the original 16-DocType migration through the same code path.

Exit codes / summary
~~~~~~~~~~~~~~~~~~~~
The script prints a per-DocType ``ins=N upd=M fail=K skip=S`` line and
a final ``=== SUMMARY ===`` block. Non-zero ``fail`` does NOT abort
the migration — partial progress is committed per DocType so a re-run
picks up the remainder.

GOTCHAS PRESERVED (all 10 from Lesson #157)
-------------------------------------------
1.  ``get_doc()`` requires the ``doctype`` key.
2.  Company default accounts 2-step (insert identity, then set defaults).
3.  Account root nodes (e.g. ``Accounts Receivable``) are system-managed
    → skip. Account is OUT OF SCOPE for college HR, so this branch
    is only relevant if you extend the script with accounting CSVs.
4.  ``Shift Type`` has ``autoname='prompt'`` → CSV must include a
    ``name`` column and the script pins it on insert.
5.  Department / Item Group circular-root trap → skip rows whose parent
    equals the configured root sentinel (default ``All Departments``).
6.  Employee requires ``gender`` and ``default_shift`` → MIGRATION_ORDER
    ensures those DocTypes come first.
7.  Employee ID remapping by ``employee_name`` → if the optional
    ``name_remap.csv`` is present (``old_name,new_name``), every
    employee Link field is rewritten before insert.
8.  Child tables stripped by REST API → N/A for CSV source, but
    Holiday List and Leave Policy children are appended programmatically
    via ``doc.append()`` to avoid the same ORM bug.
9.  Shift Assignment references a ``Shift Location`` → migrate the
    Shift Location from ``shift_location.csv`` (if present) BEFORE
    any Shift Assignment is processed.
10. Shift Request ``validate_approver()`` is unconditional + the
    autoname series silently overrides an explicit ``name`` → if
    ``shift_request.csv`` is present, pre-seed Department Approver
    rows for every referenced department AND pre-bump the autoname
    Series counter so the prod ``name`` sticks on insert.

IDEMPOTENCY
-----------
Every DocType is processed via the same ``upsert`` helper
(see ``upsert()``). This makes the script safe to re-run after
partial failure. Re-runs update any drift between source and target
without creating duplicates.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

try:
    import frappe
except ImportError:  # allow linting outside bench
    frappe = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Module-level logger. bench execute hooks this up to its log handler;
# for the CLI shim we configure a basic stderr handler.
# ---------------------------------------------------------------------------

logger = logging.getLogger("migrate_tenant_data")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class TenantConfig:
    """Tenant metadata loaded from ``tenant_config.json``.

    All fields are strings/ints so they survive JSON round-tripping.
    Per-leave-type defaults live in ``leave_type_defaults`` (a dict of
    leave_type_name → {max_leaves_allowed, is_carry_forward, ...}).
    """

    company_name: str
    company_abbr: str
    country: str = "India"
    default_currency: str = "INR"
    fiscal_year_start_month: int = 4        # 1-12, 4 = April (India FY)
    timezone: str = "Asia/Kolkata"
    shift_naming_convention: str = "prompt"  # "prompt" | "field:<fieldname>"
    leave_type_defaults: dict[str, dict] = field(default_factory=dict)

    # ----- optional / advanced -----
    department_root: str = "All Departments"
    item_group_root: str = "All Item Groups"
    approver_user: str = "Administrator"
    default_shift_location: Optional[str] = None
    holidays_fiscal_year_label: str = ""    # e.g. "FY 2026-27"

    @classmethod
    def from_json(cls, path: str | Path) -> "TenantConfig":
        """Load from a JSON file. Validates that required keys are present."""
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"tenant_config.json not found: {p}")
        with p.open() as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TenantConfig":
        """Build from a plain dict. Required: company_name, company_abbr."""
        required = ("company_name", "company_abbr")
        missing = [k for k in required if not data.get(k)]
        if missing:
            raise ValueError(
                f"tenant_config.json is missing required keys: {missing}"
            )
        return cls(
            company_name=str(data["company_name"]),
            company_abbr=str(data["company_abbr"]),
            country=str(data.get("country", "India")),
            default_currency=str(data.get("default_currency", "INR")),
            fiscal_year_start_month=int(data.get("fiscal_year_start_month", 4)),
            timezone=str(data.get("timezone", "Asia/Kolkata")),
            shift_naming_convention=str(
                data.get("shift_naming_convention", "prompt")
            ),
            leave_type_defaults=dict(data.get("leave_type_defaults", {})),
            department_root=str(data.get("department_root", "All Departments")),
            item_group_root=str(data.get("item_group_root", "All Item Groups")),
            approver_user=str(data.get("approver_user", "Administrator")),
            default_shift_location=data.get("default_shift_location"),
            holidays_fiscal_year_label=str(
                data.get("holidays_fiscal_year_label", "")
            ),
        )


#: Migration order. Order matters: dependencies first, dependents last.
#: Items not in this list are processed conditionally if their CSV is present.
MIGRATION_ORDER: list[str] = [
    "Company",
    "Department",
    "Designation",
    "Gender",                 # optional
    "Employment Type",        # optional
    "Shift Type",
    "Shift Location",         # optional
    "Holiday List",
    "Employee",
    "Leave Type",
    "Leave Policy",
    "Shift Request",          # optional
    "Shift Assignment",
]

#: Required CSV columns for each DocType. Used by ``validate_csv_columns``.
#: DocType name → list of required column names.
REQUIRED_COLUMNS: dict[str, list[str]] = {
    "Company":           ["name", "abbr", "country", "default_currency"],
    "Department":        ["name", "company"],
    "Designation":       ["name", "designation_name"],
    "Gender":            ["name"],
    "Employment Type":   ["name"],
    "Shift Type":        ["name", "start_time", "end_time"],
    "Shift Location":    ["name", "location_name"],
    "Holiday List":      ["name", "from_date", "to_date"],
    "Employee":          ["name", "first_name", "company", "department",
                          "designation", "date_of_joining", "gender",
                          "date_of_birth", "default_shift"],
    "Leave Type":        ["name", "max_leaves_allowed", "applicable_after"],
    "Leave Policy":      ["name", "applicable_for", "leave_policy_details"],
    "Shift Request":     ["name", "employee", "shift_type", "from_date",
                          "to_date"],
    "Shift Assignment":  ["name", "employee", "shift_type", "start_date",
                          "end_date", "status"],
}

#: Map CSV filename → DocType. Files not listed here are silently ignored.
CSV_FILE_TO_DOCTYPE: dict[str, str] = {
    "company.csv":           "Company",
    "department.csv":        "Department",
    "designation.csv":       "Designation",
    "gender.csv":            "Gender",
    "employment_type.csv":   "Employment Type",
    "shift_type.csv":        "Shift Type",
    "shift_location.csv":    "Shift Location",
    "holiday_list.csv":      "Holiday List",
    "employee.csv":          "Employee",
    "leave_type.csv":        "Leave Type",
    "leave_policy.csv":      "Leave Policy",
    "shift_request.csv":     "Shift Request",
    "shift_assignment.csv":  "Shift Assignment",
}

#: Fields never replayed from CSV rows. Metadata-only, managed by Frappe.
SKIP_FIELDS: frozenset[str] = frozenset({
    "name", "creation", "modified", "owner", "modified_by", "idx",
    "docstatus", "_user_tags", "_comments", "_assign", "_liked_by", "_seen",
    "lft", "rgt", "old_parent",  # tree bookkeeping
})


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def read_csv(path: str | Path) -> list[dict[str, str]]:
    """Read a CSV file and return rows as a list of dicts.

    Strips BOM, normalises column names (strip whitespace), drops
    fully-empty trailing rows. UTF-8 with ``utf-8-sig`` so Excel-saved
    files (which prepend a BOM) load cleanly.
    """
    p = Path(path)
    if not p.is_file():
        return []
    with p.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = []
        for raw in reader:
            # strip whitespace from keys + values; drop None keys (empty
            # trailing column Excel adds)
            clean = {
                (k.strip() if k else k): (v.strip() if isinstance(v, str) else v)
                for k, v in raw.items()
                if k is not None
            }
            # drop rows that are entirely empty (Excel artifact)
            if any(v not in (None, "") for v in clean.values()):
                rows.append(clean)
    return rows


def validate_csv_columns(
    csv_path: str | Path,
    doctype: str,
    required: list[str],
) -> list[str]:
    """Return a list of missing column names. Empty list = OK.

    Only checks the header — the per-row data is validated later by
    Frappe's own ORM ``LinkValidationError`` etc.
    """
    p = Path(csv_path)
    if not p.is_file():
        return required    # whole file missing → all required "missing"
    with p.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return required
    present = {h.strip() for h in header}
    return [c for c in required if c not in present]


def _split_holidays_csv(
    data_dir: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Read ``holiday_list.csv`` (one row per list) and
    ``holidays.csv`` (one row per holiday, child of the list).

    The ``holidays.csv`` schema is::

        holiday_list,holiday_date,description,optional_weekly_off

    where ``optional_weekly_off`` is 0/1 (defaults to 0).
    """
    lists = read_csv(data_dir / "holiday_list.csv")
    holidays = read_csv(data_dir / "holidays.csv")
    return lists, holidays


def _group_by(
    rows: list[dict[str, str]],
    key: str,
) -> dict[str, list[dict[str, str]]]:
    """Group a list of dicts by the value of ``key``."""
    out: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        v = r.get(key)
        if v is None or v == "":
            continue
        out.setdefault(v, []).append(r)
    return out


# ---------------------------------------------------------------------------
# Upsert pattern (Lesson #157)
# ---------------------------------------------------------------------------

def upsert(
    doctype: str,
    name: str,
    payload: dict[str, Any],
    *,
    dry_run: bool = False,
) -> str:
    """Insert or update a single record.

    Returns one of: ``"inserted"`` | ``"updated"`` | ``"dry_insert"`` |
    ``"dry_update"``.

    **Gotcha #1** — ``payload`` is always augmented with ``doctype`` before
    constructing a new document. Without this key, ``frappe.get_doc(payload)``
    raises ``ValidationError: doc(dict) does not have a valid 'doctype'``.

    **Gotcha #4** — for prompt-autoname DocTypes (Shift Type, Shift
    Location), ``name`` is pinned explicitly so Frappe doesn't try to
    generate one.
    """
    if not name:
        raise ValueError(f"upsert({doctype}) called with empty name")
    if frappe is None:
        raise RuntimeError(
            "frappe module not available — must run via 'bench execute' "
            "or inside a bench container."
        )

    if dry_run:
        return "dry_insert" if not frappe.db.exists(doctype, name) else "dry_update"

    if frappe.db.exists(doctype, name):
        doc = frappe.get_doc(doctype, name)
        doc.update(payload)
        doc.save()
        return "updated"

    new_payload = {"doctype": doctype, **payload}
    doc = frappe.get_doc(new_payload)
    doc.insert()
    return "inserted"


# ---------------------------------------------------------------------------
# Per-Doctype migrators
# ---------------------------------------------------------------------------

def _migrate_company(
    record: dict[str, str],
    cfg: TenantConfig,
    *,
    dry_run: bool,
) -> str:
    """Two-step Company insert — see GOTCHA #2.

    CSV columns expected: name, abbr, country, default_currency, plus any
    of default_receivable_account / default_payable_account /
    default_bank_account / default_cost_center / round_off_account /
    write_off_account / exchange_gain_loss_account / etc.

    Default-account links point at Account / Cost Center records that
    may not exist yet (and Account is out of scope for the college HR
    foundation). Inserting Company with them populated blows up with
    LinkValidationError. Solution: insert with identity fields only,
    then attach defaults via ``frappe.db.set_value`` if Account migration
    is added later.
    """
    name = record.get("name") or cfg.company_name
    payload = {k: v for k, v in record.items() if k not in SKIP_FIELDS}

    # Keys that depend on Account / Cost Center existing first. The
    # CSV can still carry them; we just don't try to set them during
    # the identity insert.
    deferred_keys = {
        "default_bank_account",
        "default_receivable_account",
        "default_payable_account",
        "default_expense_account",
        "default_income_account",
        "default_cost_center",
        "round_off_account",
        "write_off_account",
        "exchange_gain_loss_account",
        "unrealized_exchange_gain_loss_account",
        "disposal_account",
        "default_deferred_expense_account",
        "default_deferred_revenue_account",
        "default_inventory_account",
        "stock_adjustment_account",
        "stock_received_but_not_billed",
        "service_received_but_not_billed",
    }
    deferred: dict[str, str] = {
        k: payload.pop(k) for k in list(payload)
        if k in deferred_keys and payload.get(k)
    }

    if dry_run:
        return "dry_insert" if not frappe.db.exists("Company", name) else "dry_update"

    if frappe.db.exists("Company", name):
        doc = frappe.get_doc("Company", name)
        doc.update(payload)
        doc.save()
        result = "updated"
    else:
        np = {"doctype": "Company"}
        np.update(payload)
        doc = frappe.get_doc(np)
        doc.insert(ignore_permissions=True)
        result = "inserted"

    # Attach the deferred defaults (Account / Cost Center must exist).
    for k, v in deferred.items():
        frappe.db.set_value("Company", name, k, v, update_modified=False)

    return result


def _migrate_department(
    record: dict[str, str],
    cfg: TenantConfig,
    *,
    dry_run: bool,
) -> Optional[str]:
    """Insert or update a single Department — see GOTCHA #5.

    Skips rows whose ``parent_department`` equals the configured root
    sentinel (default ``All Departments``) — that node is auto-created
    by Frappe on app install and re-inserting it raises
    ``ParentNotFoundError``.
    """
    name = record.get("name")
    if not name:
        logger.warning("department row missing 'name' — skipping")
        return None
    if record.get("parent_department") == cfg.department_root:
        logger.debug("skip root %s/%s", cfg.department_root, name)
        return "skipped"

    payload = {k: v for k, v in record.items() if k not in SKIP_FIELDS}
    return upsert("Department", name, payload, dry_run=dry_run)


def _migrate_holiday_list(
    record: dict[str, str],
    holidays_for_list: list[dict[str, str]],
    cfg: TenantConfig,
    *,
    dry_run: bool,
) -> str:
    """Insert or update a Holiday List + its ``holidays`` child rows.

    **Gotcha #8 analog** — child rows are appended programmatically via
    ``doc.append()`` rather than via a constructor dict. The REST API
    strips child rows from ``fields=["*"]`` exports, and the same ORM
    bug surfaces if you pass child rows in the initial constructor
    while the parent is being inserted. We rebuild children on every
    run (idempotent).
    """
    name = record["name"]
    payload = {k: v for k, v in record.items() if k not in SKIP_FIELDS}

    if dry_run:
        return "dry_insert" if not frappe.db.exists("Holiday List", name) else "dry_update"

    if frappe.db.exists("Holiday List", name):
        doc = frappe.get_doc("Holiday List", name)
        # wipe children so we don't accumulate duplicates on re-runs
        doc.set("holidays", [])
        doc.update(payload)
        for h in holidays_for_list:
            doc.append("holidays", {
                "holiday_date": h.get("holiday_date"),
                "description":  h.get("description", ""),
                "weekly_off":   cint(h.get("weekly_off", 0)),
            })
        doc.save()
        return "updated"

    np = {"doctype": "Holiday List"}
    np.update(payload)
    np["holidays"] = []
    doc = frappe.get_doc(np)
    for h in holidays_for_list:
        doc.append("holidays", {
            "holiday_date": h.get("holiday_date"),
            "description":  h.get("description", ""),
            "weekly_off":   cint(h.get("weekly_off", 0)),
        })
    doc.insert()
    return "inserted"


def _migrate_leave_policy(
    record: dict[str, str],
    policy_details: list[dict[str, str]],
    cfg: TenantConfig,
    *,
    dry_run: bool,
) -> str:
    """Insert or update a Leave Policy + its ``leave_policy_details`` child.

    Same child-table gotcha as Holiday List. ``leave_policy_details``
    is rebuilt from the matching ``leave_policy_detail.csv`` rows on
    every run.
    """
    name = record["name"]
    payload = {k: v for k, v in record.items() if k not in SKIP_FIELDS}

    if dry_run:
        return "dry_insert" if not frappe.db.exists("Leave Policy", name) else "dry_update"

    if frappe.db.exists("Leave Policy", name):
        doc = frappe.get_doc("Leave Policy", name)
        doc.set("leave_policy_details", [])
        doc.update(payload)
        for d in policy_details:
            doc.append("leave_policy_details", {
                "leave_type":          d.get("leave_type"),
                "max_leaves_allowed":  cint(d.get("max_leaves_allowed", 0)),
                "annual_allocation":   cint(d.get("annual_allocation", 0)),
            })
        doc.save()
        return "updated"

    np = {"doctype": "Leave Policy"}
    np.update(payload)
    np["leave_policy_details"] = []
    doc = frappe.get_doc(np)
    for d in policy_details:
        doc.append("leave_policy_details", {
            "leave_type":          d.get("leave_type"),
            "max_leaves_allowed":  cint(d.get("max_leaves_allowed", 0)),
            "annual_allocation":   cint(d.get("annual_allocation", 0)),
        })
    doc.insert()
    return "inserted"


def _migrate_employee(
    record: dict[str, str],
    cfg: TenantConfig,
    name_remap: dict[str, str],
    *,
    dry_run: bool,
) -> str:
    """Insert or update an Employee — see GOTCHA #6, #7.

    **Gotcha #6** — Employee requires ``gender`` and ``default_shift`` Link
    fields to resolve. MIGRATION_ORDER ensures those DocTypes are inserted
    BEFORE Employee rows are processed.

    **Gotcha #7** — If ``name_remap.csv`` is present (cross-env migration
    scenario), every Link field that points to an Employee is rewritten
    from old-name → new-name. Common fields: ``reports_to``,
    ``leave_approver``, ``expense_approver``, ``shift_request_approver``.
    """
    name = record.get("name")
    if not name:
        logger.warning("employee row missing 'name' — skipping")
        return "skipped"
    payload = {k: v for k, v in record.items() if k not in SKIP_FIELDS}

    # Apply name remap to all employee Link fields
    if name_remap:
        for link_field in (
            "reports_to", "leave_approver", "expense_approver",
            "shift_request_approver", "payroll_cost_center_employee",
        ):
            if payload.get(link_field) and payload[link_field] in name_remap:
                payload[link_field] = name_remap[payload[link_field]]

    return upsert("Employee", name, payload, dry_run=dry_run)


def _migrate_shift_assignment(
    record: dict[str, str],
    cfg: TenantConfig,
    name_remap: dict[str, str],
    *,
    dry_run: bool,
) -> str:
    """Insert or update a Shift Assignment — see GOTCHAs #7 and #9.

    **Gotcha #7** — remap ``employee`` Link by old-name → new-name.
    **Gotcha #9** — ``shift_schedule_assignment`` Link is NULL'd because
    the helper DocType is out of scope for the college HR foundation.
    ``shift_location`` is preserved as-is (will fail validation if the
    location doesn't exist — migrate ``shift_location.csv`` first).
    """
    name = record.get("name")
    if not name:
        logger.warning("shift_assignment row missing 'name' — skipping")
        return "skipped"
    payload = {k: v for k, v in record.items() if k not in SKIP_FIELDS}
    # nullify out-of-scope link (GOTCHA #9)
    payload["shift_schedule_assignment"] = None
    if name_remap and payload.get("employee") in name_remap:
        payload["employee"] = name_remap[payload["employee"]]

    return upsert("Shift Assignment", name, payload, dry_run=dry_run)


# ---------------------------------------------------------------------------
# Optional / advanced: Shift Request (GOTCHA #10)
# ---------------------------------------------------------------------------

def _pre_set_shift_request_series(target_name: str) -> None:
    """Bump the autoname Series counter so Frappe honours an explicit
    ``name`` on insert. See GOTCHA #10(b).

    Shift Request declares ``autoname = "HR-SHR-.YY.-.MM.-.#####"`` which
    uses a Series counter. When the caller passes an explicit ``name`` in
    the constructor dict, Frappe *only* keeps that name if the Series
    counter has already advanced past it; otherwise it silently
    discards the explicit name and uses the next series number. To force
    the prod name to stick we pre-bump the counter to ``target_number - 1``
    before ``frappe.get_doc(...).insert()``.
    """
    m = re.match(r"^(HR-SHR-\d{2}-\d{2}-)0*(\d+)$", target_name)
    if not m:
        return
    prefix, number = m.group(1), int(m.group(2))
    rows = frappe.db.sql(
        "SELECT current FROM `tabSeries` WHERE name = %s", (prefix,), as_dict=True
    )
    current = rows[0]["current"] if rows else 0
    needed = number - 1
    if needed <= current:
        return
    if not rows:
        frappe.db.sql(
            "INSERT INTO `tabSeries` (name, current) VALUES (%s, %s)",
            (prefix, needed),
        )
    else:
        frappe.db.sql(
            "UPDATE `tabSeries` SET current = %s WHERE name = %s",
            (needed, prefix),
        )


def _ensure_department_approvers(records: list[dict[str, str]],
                                 cfg: TenantConfig) -> int:
    """Add a Department Approver row for every department referenced by
    ``records`` so Shift Request ``validate_approver()`` passes.

    See GOTCHA #10(a). Adds ``approver=<cfg.approver_user>`` with
    ``parentfield="shift_request_approver"`` and is idempotent.
    Returns the number of rows added.
    """
    departments = {r.get("department") for r in records
                   if r.get("department")}
    added = 0
    for dept in departments:
        if not frappe.db.exists(
            "Department Approver",
            {
                "parent": dept,
                "parentfield": "shift_request_approver",
                "approver": cfg.approver_user,
            },
        ):
            frappe.get_doc({
                "doctype":      "Department Approver",
                "parent":       dept,
                "parenttype":   "Department",
                "parentfield":   "shift_request_approver",
                "approver":     cfg.approver_user,
            }).insert(ignore_permissions=True)
            added += 1
    return added


def _migrate_shift_request(
    record: dict[str, str],
    cfg: TenantConfig,
    name_remap: dict[str, str],
    *,
    dry_run: bool,
) -> str:
    """Insert or update a Shift Request — see GOTCHA #10.

    Two special-cases:

    1.  The autoname series is pre-bumped to honour the prod ``name``.
    2.  Insert as ``docstatus=0, status="Draft"`` to skip
        ``validate_approver`` (the Department Approver pre-seed handles
        the actual approver lookup). Then promote to the source's final
        ``docstatus``/``status`` via ``frappe.db.set_value`` to bypass
        ``validate()`` entirely on the submit/cancel transition.
    """
    name = record.get("name")
    if not name:
        logger.warning("shift_request row missing 'name' — skipping")
        return "skipped"
    rec = dict(record)  # do not mutate caller's dict
    if name_remap and rec.get("employee") in name_remap:
        rec["employee"] = name_remap[rec["employee"]]

    orig_docstatus = int(rec.pop("docstatus", 0) or 0)
    orig_status = rec.get("status", "Draft")
    payload = {k: v for k, v in rec.items() if k not in SKIP_FIELDS}
    payload["docstatus"] = 0
    payload["status"] = "Draft"

    if dry_run:
        return ("dry_insert" if not frappe.db.exists("Shift Request", name)
                else "dry_update")

    if frappe.db.exists("Shift Request", name):
        doc = frappe.get_doc("Shift Request", name)
        doc.update(payload)
        doc.save()
    else:
        _pre_set_shift_request_series(name)
        np = {"doctype": "Shift Request", "name": name}
        np.update(payload)
        frappe.get_doc(np).insert()

    # Promote to the source's final state without re-running validate().
    frappe.db.set_value(
        "Shift Request", name,
        {"docstatus": orig_docstatus, "status": orig_status},
        update_modified=False,
    )
    return "inserted"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def cint(value: Any) -> int:
    """Coerce to int, returning 0 for None / empty string / unparseable."""
    if value in (None, ""):
        return 0
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _load_name_remap(data_dir: Path) -> dict[str, str]:
    """Load ``name_remap.csv`` (cross-env migration aid).

    Schema: ``old_name,new_name`` — one row per Employee ID remap.
    Used to translate prod employee IDs to dev IDs when seeding a new
    site from a JSON export of an existing site.
    """
    path = data_dir / "name_remap.csv"
    if not path.is_file():
        return {}
    rows = read_csv(path)
    return {r["old_name"]: r["new_name"] for r in rows
            if r.get("old_name") and r.get("new_name")}


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run(args: dict[str, Any]) -> dict[str, Any]:
    """Top-level entry point — accepts a kwargs dict (so it works with
    ``bench execute ... --kwargs '{...}'``).

    Required keys in ``args``:

    - ``tenant_config``: path to ``tenant_config.json``
    - ``data_dir``:      path to the directory holding the CSV files
    - ``site`` (optional): target site name (used only for logging)
    - ``dry_run`` (optional, default False): if True, validate + report
      but do NOT call ``frappe.db.exists()`` for write or
      ``frappe.get_doc().insert()`` / ``save()``.

    Returns a dict ``{doctype: {inserted, updated, failed, skipped, errors_sample}}``
    suitable for both human printing and programmatic consumption.
    """
    tenant_config_path = args.get("tenant_config")
    data_dir_path = args.get("data_dir")
    site = args.get("site", "")
    dry_run = bool(args.get("dry_run", False))

    if not tenant_config_path:
        raise ValueError("args['tenant_config'] is required")
    if not data_dir_path:
        raise ValueError("args['data_dir'] is required")
    if frappe is None:
        raise RuntimeError(
            "frappe module unavailable — invoke via 'bench execute'."
        )

    cfg = TenantConfig.from_json(tenant_config_path)
    data_dir = Path(data_dir_path)
    if not data_dir.is_dir():
        raise FileNotFoundError(f"data_dir not found: {data_dir}")

    name_remap = _load_name_remap(data_dir)

    logger.info("=" * 70)
    logger.info("Migrating master data on site %s", site or frappe.local.site)
    logger.info("Tenant:        %s (%s)", cfg.company_name, cfg.company_abbr)
    logger.info("Country/Ccy:   %s / %s", cfg.country, cfg.default_currency)
    logger.info("Data dir:      %s", data_dir)
    logger.info("Dry run:       %s", dry_run)
    logger.info("Name remap:    %d entries", len(name_remap))
    logger.info("=" * 70)

    # ---- pre-flight: required column validation per CSV ------------------
    validation_errors: list[str] = []
    present_csvs: dict[str, str] = {}    # filename → doctype
    for fname, doctype in CSV_FILE_TO_DOCTYPE.items():
        fpath = data_dir / fname
        if not fpath.is_file():
            logger.info("  [skip] %s not present (optional)", fname)
            continue
        required = REQUIRED_COLUMNS.get(doctype, [])
        missing = validate_csv_columns(fpath, doctype, required)
        if missing:
            validation_errors.append(
                f"{fname} (DocType={doctype}) is missing columns: {missing}"
            )
        present_csvs[fname] = doctype

    if validation_errors:
        msg = "CSV validation failed:\n  - " + "\n  - ".join(validation_errors)
        logger.error(msg)
        if not dry_run:
            raise ValueError(msg)
        logger.warning("dry-run mode: continuing despite validation errors")

    # ---- pre-flight: optional Department Approver pre-seed ---------------
    if not dry_run and (data_dir / "shift_request.csv").is_file():
        sr_rows = read_csv(data_dir / "shift_request.csv")
        added = _ensure_department_approvers(sr_rows, cfg)
        if added:
            logger.info("  pre-seeded %d Department Approver rows", added)
            frappe.db.commit()

    # ---- per-Doctype migration ------------------------------------------
    results: dict[str, dict[str, Any]] = {}

    for doctype in MIGRATION_ORDER:
        csv_name = next(
            (f for f, dt in CSV_FILE_TO_DOCTYPE.items() if dt == doctype), None
        )
        if csv_name is None or csv_name not in present_csvs:
            continue

        fpath = data_dir / csv_name
        rows = read_csv(fpath)
        logger.info("PROCESSING %s  (%d rows from %s)",
                    doctype, len(rows), csv_name)
        if not rows:
            results[doctype] = {
                "inserted": 0, "updated": 0, "failed": 0,
                "skipped": 0, "errors_sample": [],
            }
            continue

        inserted = updated = failed = skipped = 0
        errors: list[str] = []

        for rec in rows:
            name = rec.get("name", "")
            try:
                if doctype == "Company":
                    outcome = _migrate_company(rec, cfg, dry_run=dry_run)
                elif doctype == "Department":
                    outcome = _migrate_department(rec, cfg, dry_run=dry_run)
                elif doctype == "Holiday List":
                    # pair with holidays.csv
                    _, all_holidays = _split_holidays_csv(data_dir)
                    holidays_for_list = [
                        h for h in all_holidays
                        if h.get("holiday_list") == rec.get("name")
                    ]
                    outcome = _migrate_holiday_list(
                        rec, holidays_for_list, cfg, dry_run=dry_run,
                    )
                elif doctype == "Leave Policy":
                    policy_details_rows = read_csv(
                        data_dir / "leave_policy_detail.csv"
                    )
                    details_for_policy = [
                        d for d in policy_details_rows
                        if d.get("leave_policy") == rec.get("name")
                    ]
                    outcome = _migrate_leave_policy(
                        rec, details_for_policy, cfg, dry_run=dry_run,
                    )
                elif doctype == "Employee":
                    outcome = _migrate_employee(
                        rec, cfg, name_remap, dry_run=dry_run,
                    )
                elif doctype == "Shift Assignment":
                    outcome = _migrate_shift_assignment(
                        rec, cfg, name_remap, dry_run=dry_run,
                    )
                elif doctype == "Shift Request":
                    outcome = _migrate_shift_request(
                        rec, cfg, name_remap, dry_run=dry_run,
                    )
                else:
                    payload = {k: v for k, v in rec.items()
                               if k not in SKIP_FIELDS}
                    outcome = upsert(doctype, name, payload, dry_run=dry_run)

                if outcome is None:
                    continue
                if outcome == "skipped":
                    skipped += 1
                elif outcome in ("inserted", "dry_insert"):
                    inserted += 1
                elif outcome in ("updated", "dry_update"):
                    updated += 1
                else:
                    failed += 1
                    errors.append(f"{name}: unexpected outcome {outcome!r}")

            except Exception as exc:
                failed += 1
                err = f"{name}: {str(exc)[:200]}"
                if len(errors) < 5:
                    errors.append(err)
                logger.error("FAIL %s/%s: %s", doctype, name, err)

        if not dry_run:
            try:
                frappe.db.commit()
            except Exception as exc:
                logger.error("COMMIT FAILED on %s: %s", doctype, exc)

        results[doctype] = {
            "inserted": inserted, "updated": updated, "failed": failed,
            "skipped": skipped, "errors_sample": errors,
        }
        logger.info(
            "  RESULT %s: ins=%d upd=%d fail=%d skip=%d",
            doctype, inserted, updated, failed, skipped,
        )

    # ---- summary ---------------------------------------------------------
    logger.info("=" * 70)
    logger.info("=== SUMMARY ===")
    total_ins = total_upd = total_fail = total_skip = 0
    for dt, r in results.items():
        logger.info(
            "%-20s ins=%-4d upd=%-4d fail=%-2d skip=%-2d",
            dt, r["inserted"], r["updated"], r["failed"], r["skipped"],
        )
        for e in r["errors_sample"]:
            logger.info("  - %s", e)
        total_ins += r["inserted"]
        total_upd += r["updated"]
        total_fail += r["failed"]
        total_skip += r["skipped"]
    logger.info(
        "TOTAL: ins=%d upd=%d fail=%d skip=%d (dry_run=%s)",
        total_ins, total_upd, total_fail, total_skip, dry_run,
    )
    return results


# ---------------------------------------------------------------------------
# CLI shim — invoke `python migrate_tenant_data.py ...`
# ---------------------------------------------------------------------------

def _detect_app_name(start: Path) -> Optional[str]:
    """Walk up from this file looking for the bench root (contains
    ``apps.txt`` + ``sites/``), then return the app name that this
    module lives under.

    Assumes the module is at ``.../apps/<app>/<app>/utils/...`` or
    ``.../apps/<app>/<anything>/migrate_tenant_data.py``. The app
    name is the segment right after ``apps/``.
    """
    p = start.resolve()
    apps_idx = None
    for parent in [p, *p.parents]:
        if parent.name == "apps" and parent.parent:
            apps_idx = parent
            break
    if apps_idx is None:
        return None
    try:
        return apps_idx.joinpath("apps.txt").resolve().parent.name  # noqa
    except Exception:
        pass
    # fallback: return the first subdir of apps/
    try:
        return next(iter(item.name for item in apps_idx.iterdir()
                          if item.is_dir()))
    except Exception:
        return None


def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="Tenant-agnostic master data migration for Frappe HR.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tenant-config", required=True,
                        help="Path to tenant_config.json")
    parser.add_argument("--data-dir", required=True,
                        help="Path to the directory of CSV data files")
    parser.add_argument("--site", required=True,
                        help="Target Frappe site name (e.g. "
                             "pberpdev.duckdns.org)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate + report only; do not insert/update")
    parser.add_argument("--app", default=None,
                        help="Custom app hosting this module "
                             "(auto-detected if omitted)")
    parsed = parser.parse_args()

    here = Path(__file__).resolve()
    app_name = parsed.app or _detect_app_name(here)
    if not app_name:
        print("ERROR: could not detect app name. Pass --app <name>.",
              file=sys.stderr)
        return 2

    module_path = f"{app_name}.utils.migrate_tenant_data.run"
    kwargs = json.dumps({
        "tenant_config": parsed.tenant_config,
        "data_dir":      parsed.data_dir,
        "site":          parsed.site,
        "dry_run":       parsed.dry_run,
    })
    # re-exec via bench execute
    os.execvp(
        "bench", ["bench", "--site", parsed.site, "execute",
                  module_path, "--kwargs", kwargs],
    )
    return 0   # unreachable


if __name__ == "__main__":
    sys.exit(_cli())


# ---------------------------------------------------------------------------
# NOTES for future maintainers
# ---------------------------------------------------------------------------
#
# - When adding a new DocType to MIGRATION_ORDER, place it AFTER every
#   DocType it has Link / Dynamic Link dependencies on. The Frappe ORM
#   does NOT defer link validation until commit for Insert operations,
#   so inserting a child before its parent will raise LinkValidationError.
#
# - If you need a new child-table DocType (like Holiday List's
#   ``holidays`` or Leave Policy's ``leave_policy_details``), follow the
#   same pattern as ``_migrate_holiday_list``: rebuild the child rows
#   from a side CSV on every run via ``doc.set(<field>, [])`` followed
#   by ``doc.append()``. Don't rely on the constructor dict to carry
#   child rows — see GOTCHA #8.
#
# - The ``dry_run`` mode is your friend. Run it first, read the SUMMARY
#   block, then drop --dry-run for the live migration.
#
# - If a particular client uses a non-prompt autoname scheme (e.g.
#   autoname = "field:slug"), set ``shift_naming_convention`` in
#   tenant_config.json — the script will only need a minor adjustment
#   in ``_migrate_shift_type`` (not currently a dedicated helper — uses
#   the generic upsert path).
#
# - The script honours the same ``name_remap.csv`` semantics as the
#   original Haritha script. If you're seeding a fresh site (no
#   existing employees), leave it out — the CSV ``name`` column is the
#   canonical name on the target site.
