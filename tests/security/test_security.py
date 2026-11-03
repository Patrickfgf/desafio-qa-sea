"""Security-oriented API tests. The app has no authentication, so "without credentials" means a
plain request. Writes only touch records created by ``create_employee`` (``QA-AUTO-`` names).
"""

import json

import pytest

from support.api_client import describe
from support.factory import as_payload, build_employee

pytestmark = pytest.mark.security

DENIED = (401, 403)
ORIGIN = "https://evil.example"
SECURITY_HEADERS = (
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
)
NO_CREDENTIALS_REASON = "BUG-004: API cria, altera e apaga registros sem autenticação"


def _register_id(created_ids, resp):
    """Register the id of a created record BEFORE the caller asserts."""
    try:
        body = resp.json()
    except ValueError:
        return
    if isinstance(body, dict) and "id" in body:
        created_ids.append(body["id"])


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-002: API expõe CPF, RG e nascimento sem autenticação",
)
def test_list_requires_authentication(api, create_employee):
    created = create_employee()

    # Filter by our own id so third-party records are never loaded (rule 6).
    resp = api.list(params={"id": created["id"]})

    # Collection response: status and count only, never the body.
    count = len(resp.json()) if resp.status_code == 200 else 0
    assert resp.status_code in DENIED, (
        f"GET list without credentials -> {resp.status_code}, {count} record(s)"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-002: API expõe CPF, RG e nascimento sem autenticação",
)
def test_record_does_not_expose_full_cpf(api, create_employee):
    sent = build_employee()
    created = create_employee(**sent)

    resp = api.get(created["id"])

    assert resp.status_code == 200, describe(resp)
    assert resp.json()["state"]["employee"]["cpf"] != sent["cpf"], describe(resp)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=NO_CREDENTIALS_REASON)
def test_create_requires_authentication(api, created_ids):
    resp = api.create(as_payload(build_employee()))
    _register_id(created_ids, resp)

    assert resp.status_code in DENIED, describe(resp)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=NO_CREDENTIALS_REASON)
@pytest.mark.parametrize("method", ["replace", "patch"])
def test_update_requires_authentication(api, create_employee, method):
    created = create_employee()
    body = as_payload(build_employee(name=created["state"]["employee"]["name"]))

    resp = getattr(api, method)(created["id"], body)

    assert resp.status_code in DENIED, describe(resp)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=NO_CREDENTIALS_REASON)
def test_delete_requires_authentication(api, create_employee):
    created = create_employee()

    resp = api.delete(created["id"])

    assert resp.status_code in DENIED, describe(resp)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-020: CORS inválido (*,*) e POST text/plain aceito",
)
def test_cors_allow_origin_is_single_value(api, create_employee):
    created = create_employee()

    resp = api.session.get(
        api.url_for(created["id"]), headers={"Origin": ORIGIN}, timeout=api.timeout
    )

    allow_origin = resp.headers.get("access-control-allow-origin")
    assert resp.status_code == 200, describe(resp)
    assert allow_origin is not None, describe(resp)
    assert "," not in allow_origin, (
        f"access-control-allow-origin has several values: {allow_origin}"
    )
    assert allow_origin in ("*", ORIGIN), f"access-control-allow-origin: {allow_origin}"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-020: CORS inválido (*,*) e POST text/plain aceito",
)
def test_create_rejects_non_json_content_type(api, created_ids):
    payload = json.dumps(as_payload(build_employee()))

    resp = api.session.post(
        api.url_for(),
        data=payload,
        headers={"Content-Type": "text/plain"},
        timeout=api.timeout,
    )
    _register_id(created_ids, resp)

    assert 400 <= resp.status_code < 500, describe(resp)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-021: Sem cabeçalhos de segurança e com x-powered-by",
)
def test_security_headers_present(api):
    # HEAD /employees returns no body; GET / is the static SPA shell (no records).
    responses = {
        "HEAD /employees": api.session.head(api.url_for(), timeout=api.timeout),
        "GET /": api.session.get(api.base_url + "/", timeout=api.timeout),
    }

    problems = []
    for label, resp in responses.items():
        missing = [h for h in SECURITY_HEADERS if h not in resp.headers]
        if missing:
            problems.append(f"{label} missing {missing}")
        if "x-powered-by" in resp.headers:
            problems.append(f"{label} exposes x-powered-by")
    assert problems == [], "; ".join(problems)
