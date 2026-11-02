from uuid import uuid4

import pytest

from support.api_client import describe, mismatched_fields
from support.factory import TEST_PREFIX, as_payload, build_employee

pytestmark = pytest.mark.api


def test_create_returns_201_and_echoes_payload(api, created_ids):
    sent = build_employee()

    resp = api.create(as_payload(sent))
    if resp.status_code == 201:
        created_ids.append(resp.json()["id"])

    assert resp.status_code == 201, describe(resp)
    body = resp.json()
    assert "id" in body, describe(resp)
    assert mismatched_fields(sent, body["state"]["employee"]) == [], describe(resp)


def test_get_by_id_returns_created_record(api, create_employee):
    created = create_employee()

    resp = api.get(created["id"])

    assert resp.status_code == 200, describe(resp)
    got = resp.json()
    assert got.get("id") == created["id"], describe(resp)
    assert mismatched_fields(created["state"]["employee"], got["state"]["employee"]) == [], (
        describe(resp)
    )


def test_put_replaces_record(api, create_employee):
    created = create_employee()
    employee = created["state"]["employee"]
    new_role = "Cargo 99" if employee["role"] != "Cargo 99" else "Cargo 98"

    put = api.replace(created["id"], as_payload({**employee, "role": new_role}))
    got = api.get(created["id"])

    assert put.status_code == 200, describe(put)
    assert got.status_code == 200, describe(got)
    assert got.json()["state"]["employee"]["role"] == new_role, describe(got)


def test_delete_removes_record(api, create_employee):
    created = create_employee()

    deleted = api.delete(created["id"])
    after = api.get(created["id"])

    assert deleted.status_code == 200, describe(deleted)
    assert after.status_code == 404, describe(after)


def test_accented_name_round_trips(api, create_employee):
    name = f"{TEST_PREFIX}João Conceição Ávila {uuid4().hex[:6]}"
    created = create_employee(name=name)

    resp = api.get(created["id"])

    assert resp.status_code == 200, describe(resp)
    assert resp.json()["state"]["employee"]["name"] == name, describe(resp)
