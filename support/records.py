"""Read back a record created through the UI, by exact name (never by listing the base)."""

from __future__ import annotations

from support.api_client import EmployeesClient, describe


def find_saved_record(api: EmployeesClient, name: str) -> dict:
    """The single stored record whose ``state.employee.name`` is ``name`` (our own record)."""
    ids = api.find_ids_by_name(name)
    assert len(ids) == 1, f"expected exactly 1 record with the test name, found {len(ids)}"
    resp = api.get(ids[0])
    assert resp.status_code == 200, describe(resp)
    return resp.json()
