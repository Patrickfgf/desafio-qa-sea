"""Masked profile of the shared employee base: aggregates only, never names or raw CPFs.

This is the only sanctioned way to look at the whole list. It downloads it once (one GET) and
prints counts; free-text values outside an allowlist are collapsed to ``<other>``.
"""

import json
import os
import re
import sys
from collections import Counter
from datetime import date

from support.api_client import BASE_URL_DEFAULT, EmployeesClient, describe
from support.cpf import is_valid_cpf
from support.factory import ACTIVITIES, EMPLOYEE_FIELDS, EPI_LABELS, ROLES, TEST_PREFIX

TOP_N = 10
MISSING = "missing"
OTHER = "<other>"
UNKNOWN = "<unknown>"
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_KNOWN_KEYS = frozenset(EMPLOYEE_FIELDS)
_ROLES = frozenset(ROLES)
_ACTIVITIES = frozenset(ACTIVITIES)
_EPIS = frozenset(EPI_LABELS)


def _employee_of(record) -> dict:
    """Employee dict of a record, or ``{}`` when the shape is not as expected."""
    state = record.get("state") if isinstance(record, dict) else None
    employee = state.get("employee") if isinstance(state, dict) else None
    return employee if isinstance(employee, dict) else {}


def _is_blank(value) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _digits(value: str) -> str:
    return "".join(ch for ch in value if ch.isdigit())


def _is_future_birthday(value, today: date) -> bool:
    if not isinstance(value, str) or not _ISO_DATE.fullmatch(value):
        return False
    try:
        return date.fromisoformat(value) > today
    except ValueError:
        return False


def _top_allowed(employees: list[dict], field: str, allowed: frozenset[str]) -> list[list]:
    """Top values of ``field``; anything outside ``allowed`` (or "") is collapsed to ``<other>``.

    Allowlist, not name detection: third parties write free text here, and a person's name
    must never reach stdout.
    """

    def bucket(employee: dict) -> str:
        if field not in employee:
            return MISSING
        value = employee[field]
        return value if isinstance(value, str) and (value == "" or value in allowed) else OTHER

    counts = Counter(bucket(e) for e in employees)
    return [[value, count] for value, count in counts.most_common(TOP_N)]


def _active_bucket(employee: dict) -> str:
    """Closed enum for ``isActive``: free text from third parties never reaches the output."""
    if "isActive" not in employee:
        return MISSING
    value = employee["isActive"]
    if value is True:
        return "true"
    if value is False:
        return "false"
    return OTHER


def profile(records: list, today: date) -> dict:
    """Pure aggregate of ``records``; tolerates any malformed third-party record."""
    employees = [_employee_of(r) for r in records]
    cpfs = [e.get("cpf") for e in employees]
    cpf_counts = Counter(_digits(c) for c in cpfs if isinstance(c, str) and _digits(c))
    key_sets = Counter(
        tuple(sorted(k if k in _KNOWN_KEYS else UNKNOWN for k in e)) for e in employees
    )
    return {
        "total": len(records),
        "id_types": dict(
            Counter(
                type(r.get("id")).__name__ if isinstance(r, dict) else "missing" for r in records
            )
        ),
        "employee_key_sets": [[list(k), n] for k, n in key_sets.most_common(TOP_N)],
        "invalid_cpf": sum(1 for c in cpfs if not isinstance(c, str) or not is_valid_cpf(c)),
        "duplicate_cpf": sum(1 for n in cpf_counts.values() if n > 1),
        "future_birthdays": sum(_is_future_birthday(e.get("birthDay"), today) for e in employees),
        "uses_epi_without_ca": sum(
            e.get("usesEpi") is True and _is_blank(e.get("caNumber")) for e in employees
        ),
        "no_epi_with_ca": sum(
            e.get("usesEpi") is False and not _is_blank(e.get("caNumber")) for e in employees
        ),
        "is_active": dict(Counter(_active_bucket(e) for e in employees)),
        "roles": _top_allowed(employees, "role", _ROLES),
        "activities": _top_allowed(employees, "activity", _ACTIVITIES),
        "epis": _top_allowed(employees, "epi", _EPIS),
        "test_prefixed": sum(
            isinstance(e.get("name"), str) and e["name"].startswith(TEST_PREFIX) for e in employees
        ),
    }


def main() -> None:
    base_url = os.environ.get("APP_BASE_URL", BASE_URL_DEFAULT)
    resp = EmployeesClient(base_url).list()
    if resp.status_code != 200:
        raise RuntimeError(f"Unexpected list status: {describe(resp)}")
    body = resp.json()
    records = body.get("data") if isinstance(body, dict) else body
    if not isinstance(records, list):
        raise RuntimeError("Unexpected list shape: neither an array nor {data: [...]}")
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(profile(records, date.today()), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
