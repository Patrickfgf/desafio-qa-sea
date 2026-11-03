"""Thin client for the /employees REST API (json-server v1) plus safe response formatting."""

from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import quote

import requests

from support.pii import mask_text


class PreconditionError(RuntimeError):
    """A test's setup failed (not the behaviour under test).

    Deliberately not an ``AssertionError``: ``xfail(raises=AssertionError)`` must not
    swallow a broken environment, a reset base or a failed setup call as a known bug.
    """


BASE_URL_DEFAULT = "https://analista-teste.seatecnologia.com.br"
DESCRIBE_MAX_CHARS = 500
_ALREADY_GONE = (200, 204, 404)

EmployeeId = str | int


class EmployeesClient:
    """One ``requests.Session`` per client; every id is URL-escaped (ids may be int or str)."""

    def __init__(self, base_url: str, timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def url_for(self, employee_id: EmployeeId | None = None) -> str:
        url = f"{self.base_url}/employees"
        if employee_id is None:
            return url
        return f"{url}/{quote(str(employee_id), safe='')}"

    def list(self, params: dict | None = None) -> requests.Response:
        return self.session.get(self.url_for(), params=params, timeout=self.timeout)

    def get(self, employee_id: EmployeeId) -> requests.Response:
        return self.session.get(self.url_for(employee_id), timeout=self.timeout)

    def create(self, payload: dict) -> requests.Response:
        return self.session.post(self.url_for(), json=payload, timeout=self.timeout)

    def replace(self, employee_id: EmployeeId, payload: dict) -> requests.Response:
        return self.session.put(self.url_for(employee_id), json=payload, timeout=self.timeout)

    def patch(self, employee_id: EmployeeId, payload: dict) -> requests.Response:
        return self.session.patch(self.url_for(employee_id), json=payload, timeout=self.timeout)

    def delete(self, employee_id: EmployeeId) -> requests.Response:
        return self.session.delete(self.url_for(employee_id), timeout=self.timeout)

    def options(self) -> requests.Response:
        return self.session.options(self.url_for(), timeout=self.timeout)

    def find_ids_by_name(self, name: str) -> list[EmployeeId]:
        """Ids of records whose ``state.employee.name`` is exactly ``name``."""
        return self.find_ids_by_names({name})

    def find_ids_by_names(self, names: set[str]) -> list[EmployeeId]:
        """One server-side exact-name filter GET per name; the shared base is never listed.

        The server filter is exact equality (there is no prefix filter); the name is still
        re-checked client-side so a looser server never widens what the caller deletes.
        """
        ids = []
        for name in sorted(names):
            resp = self.list(params={"state.employee.name": name})
            if resp.status_code != 200:
                raise PreconditionError(f"Unexpected list status: {describe(resp)}")
            for record in _records_of(resp.json()):
                employee = _employee_of(record)
                if employee is not None and employee.get("name") == name and "id" in record:
                    ids.append(record["id"])
        return ids


def _records_of(body) -> list:
    """The record list of a collection response: a bare array or a paginated ``{"data": [...]}``."""
    records = body.get("data", []) if isinstance(body, dict) else body
    return records if isinstance(records, list) else []


def _employee_of(record) -> dict | None:
    """Return ``record["state"]["employee"]`` or None when the shape is not as expected."""
    if not isinstance(record, dict) or not isinstance(record.get("state"), dict):
        return None
    employee = record["state"].get("employee")
    return employee if isinstance(employee, dict) else None


def mismatched_fields(expected: dict, actual: dict) -> list[str]:
    """Sorted names of keys that differ, are missing or extra; never exposes values.

    Use in asserts instead of ``==`` on dicts: pytest's assertion introspection prints both
    operands on failure, which would put raw PII in the terminal and the HTML report.
    """
    keys = set(expected) | set(actual)
    return sorted(
        k for k in keys if k not in expected or k not in actual or expected[k] != actual[k]
    )


def describe(resp: requests.Response) -> str:
    """``METHOD url -> status: body``; the body is masked BEFORE truncation (no partial CPF)."""
    request = resp.request
    method = request.method if request is not None else "?"
    url = resp.url or (request.url if request is not None else "?")
    body = mask_text(resp.text)[:DESCRIBE_MAX_CHARS]
    return f"{method} {url} -> {resp.status_code}: {body}"


def delete_quietly(client, ids: Iterable[EmployeeId]) -> list[EmployeeId]:
    """Delete each id; return the ids that may still exist (the caller warns about them).

    A 404 is ambiguous: the record is gone, or its id is an int that json-server v1 cannot
    reach by route (``/employees/7`` -> 404 while ``?id=7`` still lists it). Only on 404 the
    id is confirmed with one ``?id=`` filter GET; a failed confirmation counts as a leftover.
    """
    leftovers = []
    for employee_id in ids:
        try:
            status = client.delete(employee_id).status_code
        except requests.RequestException:
            leftovers.append(employee_id)
            continue
        if status not in _ALREADY_GONE or (status == 404 and _still_listed(client, employee_id)):
            leftovers.append(employee_id)
    return leftovers


def _still_listed(client, employee_id: EmployeeId) -> bool:
    """True when ``?id=`` still finds the record, or when that cannot be confirmed."""
    try:
        resp = client.list(params={"id": employee_id})
    except requests.RequestException:
        return True
    if resp.status_code != 200:
        return True
    try:
        return bool(_records_of(resp.json()))
    except ValueError:
        return True


def require_status(resp: requests.Response, expected: int) -> None:
    """Raise PreconditionError (never xfail-able) if a setup call returned another status."""
    if resp.status_code != expected:
        raise PreconditionError(f"Precondition failed, expected {expected}: {describe(resp)}")
