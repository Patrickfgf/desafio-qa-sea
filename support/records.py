"""Read back a record created through the UI, by exact name (never by listing the base)."""

from __future__ import annotations

from support.api_client import EmployeesClient, PreconditionError, require_status


def find_saved_record(api: EmployeesClient, name: str) -> dict:
    """The single stored record whose ``state.employee.name`` is ``name`` (our own record)."""
    ids = api.find_ids_by_name(name)
    if len(ids) != 1:
        raise PreconditionError(f"expected exactly 1 record with the test name, found {len(ids)}")
    resp = api.get(ids[0])
    require_status(resp, 200)
    return resp.json()
