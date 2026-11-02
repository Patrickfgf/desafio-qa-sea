"""HTTP evidence helpers: a masked, bounded text record of one request/response exchange.

Ownership rule (response bodies): a JSON record (``{"state": {"employee": {...}}}`` or a bare
employee dict) is OURS when its employee name is a str starting with ``TEST_PREFIX``
(``QA-AUTO-``). It is THIRD-PARTY when it is not ours and carries a non-empty name, cpf, rg or
birthDay. Third-party records are OMITTED from the evidence (replaced by a notice), never
masked field by field. Records with none of those fields are neutral and kept.

Our own synthetic values are kept raw on purpose (e.g. an invalid cpf ``abcdefghijk`` or
birthDay ``2023-02-30`` is the evidence), with CPF-only masking applied afterwards
(``support.pii.mask_text``, belt and braces for valid CPF-shaped values). JSON unicode-escaped
digits are not matched by that masking, hence ``ensure_ascii=False``.

Parsed JSON bodies are re-serialized compactly (``json.dumps(..., ensure_ascii=False)``), masked
and only then truncated, so a CPF cut at the boundary can never leak an unmasked partial tail.
Non-JSON bodies and request bodies (built by the test itself) get ``mask_text`` only. The
request line is percent-decoded before masking so encoded separators cannot dodge the pattern.
Header values are masked too.
"""

import json
from pathlib import Path
from urllib.parse import unquote

import requests

from support.factory import TEST_PREFIX
from support.pii import mask_text

MAX_RESPONSE_BODY_CHARS = 2000
EMPTY_BODY_MARKER = "(sem corpo)"
_PII_FIELDS = ("name", "cpf", "rg", "birthDay")
_THIRD_PARTY_ONE = "(registro de terceiro omitido da evidência)"
_THIRD_PARTY_MANY = "({n} registro(s) de terceiros omitido(s) da evidência)"
_REQUEST_HEADERS = ("content-type",)
_RESPONSE_HEADERS = (
    "content-type",
    "access-control-allow-origin",
    "access-control-allow-methods",
    "x-powered-by",
)


def _masked_request_body(resp: requests.Response) -> str:
    body = resp.request.body
    if body is None or body == b"" or body == "":
        return EMPTY_BODY_MARKER
    text = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
    return mask_text(text)


def _header_lines(headers, names: tuple[str, ...]) -> list[str]:
    return [mask_text(f"{name}: {headers[name]}") for name in names if name in headers]


def _employee_of(record):
    """Return the employee dict of a record (wrapped or bare), or None if not a record."""
    if not isinstance(record, dict):
        return None
    state = record.get("state")
    if isinstance(state, dict) and isinstance(state.get("employee"), dict):
        return state["employee"]
    if any(field in record for field in _PII_FIELDS):
        return record
    return None


def _is_third_party(record) -> bool:
    employee = _employee_of(record)
    if employee is None:
        return False
    name = employee.get("name")
    if isinstance(name, str) and name.startswith(TEST_PREFIX):
        return False
    return any(employee.get(field) not in (None, "") for field in _PII_FIELDS)


def _filter_records(value):
    """Return (kept_value, omitted_count); a lone third-party record becomes the notice text."""
    if isinstance(value, list):
        kept = [item for item in value if not _is_third_party(item)]
        return kept, len(value) - len(kept)
    if isinstance(value, dict) and isinstance(value.get("data"), list):
        kept, omitted = _filter_records(value["data"])
        return {**value, "data": kept}, omitted
    if _is_third_party(value):
        return _THIRD_PARTY_ONE, 0
    return value, 0


def _masked_response_body(text: str) -> str:
    try:
        parsed = json.loads(text)
    except ValueError:
        return mask_text(text)[:MAX_RESPONSE_BODY_CHARS]
    kept, omitted = _filter_records(parsed)
    body = kept if isinstance(kept, str) else json.dumps(kept, ensure_ascii=False)
    body = mask_text(body)[:MAX_RESPONSE_BODY_CHARS]
    if not omitted:
        return body
    return body + "\n" + _THIRD_PARTY_MANY.format(n=omitted)


def format_exchange(resp: requests.Response) -> str:
    """Render request line, request content-type, masked request body, status line, selected
    response headers and the masked response body (cut at 2000 chars after masking).

    An empty request body is shown as ``(sem corpo)``.
    """
    request = resp.request
    lines = [mask_text(unquote(f"{request.method} {request.url}"))]
    lines += _header_lines(request.headers, _REQUEST_HEADERS)
    lines.append(_masked_request_body(resp))
    lines.append(f"HTTP {resp.status_code} {resp.reason}")
    lines += _header_lines(resp.headers, _RESPONSE_HEADERS)
    lines.append(_masked_response_body(resp.text))
    return "\n".join(lines) + "\n"


def save_exchange(resp: requests.Response, path: Path) -> Path:
    """Write ``format_exchange(resp)`` to ``path`` (utf-8), creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_exchange(resp), encoding="utf-8")
    return path
