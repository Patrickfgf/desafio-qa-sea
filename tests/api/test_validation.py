"""Negative API tests: input validation, schema, PUT/PATCH semantics, pagination, parse errors.

Every test documents a known defect as a strict xfail. Each record sent here carries the
``QA-AUTO-`` name prefix and its id is registered for cleanup right after the POST, because the
API (wrongly) accepts most of these payloads and would otherwise leave them behind.
"""

from datetime import date, timedelta

import pytest

from support.api_client import describe, require_status
from support.factory import TEST_PREFIX, as_payload, build_employee

pytestmark = pytest.mark.api

REJECTED = (400, 422)
SYMBOLS_ONLY_CA = "@!#$&&$#"  # inert text that only looks odd (BUG-025)
INVALID_CPF_CHECKSUM = "52998224726"  # valid CPF 52998224725 with a wrong last check digit
UNSENT_FIELDS = (
    "name",
    "gender",
    "cpf",
    "birthDay",
    "rg",
    "role",
    "usesEpi",
    "activity",
    "epi",
    "caNumber",
)


def _post_and_register(api, created_ids, payload):
    """POST ``payload``; register the new id for cleanup BEFORE the caller asserts."""
    resp = api.create(payload)
    try:
        body = resp.json()
    except ValueError:
        body = None
    if isinstance(body, dict) and "id" in body:
        created_ids.append(body["id"])
    return resp


@pytest.mark.xfail(
    strict=True, raises=AssertionError, reason="BUG-008: CPF aceito sem validação de conteúdo"
)
def test_create_rejects_invalid_cpf_checksum(api, created_ids):
    resp = _post_and_register(
        api, created_ids, as_payload(build_employee(cpf=INVALID_CPF_CHECKSUM))
    )

    assert resp.status_code in REJECTED, describe(resp)


@pytest.mark.xfail(
    strict=True, raises=AssertionError, reason="BUG-008: CPF aceito sem validação de conteúdo"
)
def test_create_rejects_cpf_with_letters(api, created_ids):
    resp = _post_and_register(api, created_ids, as_payload(build_employee(cpf="abcdefghijk")))

    assert resp.status_code in REJECTED, describe(resp)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-010: Data de nascimento sem validação de intervalo",
)
def test_create_rejects_future_birth_date(api, created_ids):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    resp = _post_and_register(api, created_ids, as_payload(build_employee(birthDay=tomorrow)))

    assert resp.status_code in REJECTED, describe(resp)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-011: API não valida schema, tipos nem campos extras",
)
def test_create_rejects_missing_required_fields(api, created_ids):
    # Keeps state.employee (and our name prefix); never send a body without it (BUG-005).
    name = build_employee()["name"]
    payload = {"state": {"employee": {"name": name}}}

    resp = _post_and_register(api, created_ids, payload)

    assert resp.status_code in REJECTED, describe(resp)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-011: API não valida schema, tipos nem campos extras",
)
@pytest.mark.parametrize(
    ("field", "value"),
    [("role", "Cargo 99"), ("epi", "nao-existe"), ("isActive", "false")],
    ids=["role-out-of-domain", "epi-out-of-domain", "isActive-string"],
)
def test_create_rejects_out_of_domain_values(api, created_ids, field, value):
    resp = _post_and_register(api, created_ids, as_payload(build_employee(**{field: value})))

    assert resp.status_code in REJECTED, describe(resp)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-011: API não valida schema, tipos nem campos extras",
)
def test_create_rejects_unknown_fields(api, created_ids):
    payload = as_payload({**build_employee(), "isAdmin": True})

    resp = _post_and_register(api, created_ids, payload)

    if resp.status_code in REJECTED:
        return
    assert resp.status_code == 201, describe(resp)
    stored = api.get(resp.json()["id"])
    require_status(stored, 200)
    assert "isAdmin" not in stored.json()["state"]["employee"], describe(stored)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-011: API não valida schema, tipos nem campos extras",
)
def test_put_rejects_missing_required_fields(api, create_employee):
    created = create_employee()
    name = created["state"]["employee"]["name"]
    assert name.startswith(TEST_PREFIX)

    resp = api.replace(created["id"], {"state": {"employee": {"name": name}}})

    assert resp.status_code in REJECTED, describe(resp)
    after = api.get(created["id"])
    require_status(after, 200)
    assert "cpf" in after.json()["state"]["employee"], describe(after)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-014: PATCH em state apaga os campos não enviados",
)
def test_patch_preserves_unsent_fields(api, create_employee):
    created = create_employee()

    patch = api.patch(created["id"], {"state": {"employee": {"isActive": False}}})
    after = api.get(created["id"])

    require_status(patch, 200)
    require_status(after, 200)
    employee = after.json()["state"]["employee"]
    missing = [f for f in UNSENT_FIELDS if f not in employee]
    assert missing == [], f"Fields lost after PATCH: {missing}; {describe(after)}"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-018: Paginação inconsistente em casos-limite",
)
def test_pagination_beyond_last_page_returns_empty_data(api, create_employee):
    created = create_employee()

    # The id filter combines with pagination (checked on first run): one match, one page.
    resp = api.list(params={"id": created["id"], "_page": 2, "_per_page": 1})

    require_status(resp, 200)
    body = resp.json()
    data = body.get("data") if isinstance(body, dict) else None
    # Collection response: assert on counts only, never on its content.
    assert isinstance(data, list), f"GET list -> {resp.status_code}: no data array"
    assert len(data) == 0, f"Page 2 of 1 item returned {len(data)} item(s), expected 0"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-019: JSON malformado devolve 500 em vez de 400",
)
def test_malformed_json_returns_400(api, created_ids):
    # Never an empty body: that creates a bare {id} record (BUG-005 trigger).
    resp = api.session.post(
        api.url_for(),
        data="not json",
        headers={"Content-Type": "application/json"},
        timeout=api.timeout,
    )
    try:
        body = resp.json()
    except ValueError:
        body = None
    if isinstance(body, dict) and "id" in body:
        created_ids.append(body["id"])

    assert resp.status_code == 400, f"POST malformed JSON -> {resp.status_code}"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-025: CA aceita símbolos",
)
def test_create_rejects_symbols_in_ca_number(api, created_ids):
    resp = _post_and_register(
        api, created_ids, as_payload(build_employee(caNumber=SYMBOLS_ONLY_CA))
    )

    assert resp.status_code in REJECTED, describe(resp)
