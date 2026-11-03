"""HTTP evidence helpers: a masked, bounded text record of one request/response exchange.

Ownership rule (response bodies): a JSON record (``{"state": {"employee": {...}}}`` or a bare
employee dict) is OURS when its employee name is a str starting with ``TEST_PREFIX``
(``QA-AUTO-``). It is THIRD-PARTY when it is not ours and carries a non-empty name, cpf, rg or
birthDay. Records with none of those fields are neutral and kept. The check is fail-closed:
field names are compared case-insensitively, PII is looked for in the record, its ``state`` and
its ``state.employee``, a record is ours only if EVERY PII-bearing dict in it is ours, and a
non-dict ``state.employee`` counts as third-party.

The parsed body is walked recursively (list, json-server envelope ``{data: [...], ...}``, single
record, any wrapper key or nesting). Third-party records are REMOVED from their parent and
counted: a notice line ``(N registro(s) de terceiros omitido(s) da evidência)`` follows the
body; a body that is itself one third-party record becomes only
``(registro de terceiro omitido da evidência)``. Third-party records are omitted, never masked
field by field. JSON-in-a-string is decoded (up to 3 levels) before walking. A body that is not
JSON (or too deeply nested to parse) and contains PII-like keys (name/cpf/rg/birthDay followed
by ``:`` or ``=``) is omitted entirely; otherwise it gets ``mask_text`` only.

Limitation: ownership depends only on the RESPONSE name. If the app echoes back an empty,
non-str or non-prefixed name for our own record, that record is treated as third-party and
omitted; the request body (built by the test) still shows what was sent.

Our own synthetic values are kept raw on purpose (e.g. an invalid cpf ``abcdefghijk`` or
birthDay ``2023-02-30`` is the evidence), with CPF-only masking applied afterwards
(``support.pii.mask_text``, belt and braces for valid CPF-shaped values). JSON unicode-escaped
digits are not matched by that masking, hence ``ensure_ascii=False``.

Kept JSON is re-serialized on one line with ``json.dumps`` defaults (``ensure_ascii=False``),
masked and only then truncated to 2000 chars, so a CPF cut at the boundary can never leak an
unmasked partial tail; the omission notice is appended after the cut. Request bodies (built by
the test itself) get ``mask_text`` only. The request line is percent-decoded (until stable, max
3 passes) before masking, so encoded separators cannot dodge the pattern; as a side effect
``%26``/``%3D`` appear as live separators in the evidence line. Header values are masked too.
"""

import json
import re
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
_MAX_JSON_UNWRAP = 3
_MAX_URL_DECODES = 3
_UNPARSED = object()
_NON_JSON_PII_NOTICE = "(corpo não-JSON com campos de PII omitido da evidência)"
_PII_KEY_PATTERN = re.compile(r"(?:name|cpf|rg|birthday)[\"']?\s*[:=]", re.IGNORECASE)
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


def _get(mapping: dict, key: str):
    """Case-insensitive dict lookup (a stranger's ``Name``/``CPF`` must not dodge the rule)."""
    lowered = key.lower()
    for candidate, value in mapping.items():
        if isinstance(candidate, str) and candidate.lower() == lowered:
            return value
    return None


def _pii_dicts(record: dict) -> list[dict] | None:
    """Dicts of a record that may carry PII (itself, state, state.employee).

    Returns None when ``state.employee`` is present but not a dict (unknown shape: fail closed).
    """
    found = [record]
    state = _get(record, "state")
    if isinstance(state, dict):
        found.append(state)
        employee = _get(state, "employee")
        if isinstance(employee, dict):
            found.append(employee)
        elif employee is not None:
            return None
    return found


def _has_pii(mapping: dict) -> bool:
    return any(_get(mapping, field) not in (None, "", [], {}) for field in _PII_FIELDS)


def _is_ours(mapping: dict) -> bool:
    name = _get(mapping, "name")
    return isinstance(name, str) and name.startswith(TEST_PREFIX)


def _is_third_party(node) -> bool:
    """A dict is third-party unless every PII-bearing dict inside it is OURS (fail closed)."""
    if not isinstance(node, dict):
        return False
    dicts = _pii_dicts(node)
    if dicts is None:
        return True
    return any(_has_pii(d) and not _is_ours(d) for d in dicts)


_DROPPED = object()


def _filter_records(node):
    """Walk the whole JSON tree; return (kept, omitted_count).

    Any dict that is third-party (at any depth, under any key) is removed from its parent list
    or dict; a root that is itself third-party comes back as ``_DROPPED``.
    """
    if _is_third_party(node):
        return _DROPPED, 1
    omitted = 0
    if isinstance(node, list):
        kept_list = []
        for item in node:
            kept, count = _filter_records(item)
            omitted += count
            if kept is not _DROPPED:
                kept_list.append(kept)
        return kept_list, omitted
    if isinstance(node, dict):
        kept_dict = {}
        for key, item in node.items():
            kept, count = _filter_records(item)
            omitted += count
            if kept is not _DROPPED:
                kept_dict[key] = kept
        return kept_dict, omitted
    return node, 0


def _parse_json(text: str):
    """json.loads, decoding JSON-in-a-string a few times; raises ValueError/RecursionError."""
    value = json.loads(text)
    for _ in range(_MAX_JSON_UNWRAP):
        if not isinstance(value, str):
            break
        try:
            value = json.loads(value)
        except ValueError:
            break
    return value


def _masked_response_body(text: str) -> str:
    try:
        parsed = _parse_json(text)
    except (ValueError, RecursionError):
        parsed = _UNPARSED
    if parsed is _UNPARSED or isinstance(parsed, str):
        shown = text if parsed is _UNPARSED else json.dumps(parsed, ensure_ascii=False)
        # str(parsed) is a no-op here (parsed is a str); it only narrows the type for Pyright.
        if _PII_KEY_PATTERN.search(text if parsed is _UNPARSED else str(parsed)):
            return _NON_JSON_PII_NOTICE
        return mask_text(shown)[:MAX_RESPONSE_BODY_CHARS]
    kept, omitted = _filter_records(parsed)
    if kept is _DROPPED:
        return _THIRD_PARTY_ONE
    body = mask_text(json.dumps(kept, ensure_ascii=False))[:MAX_RESPONSE_BODY_CHARS]
    if not omitted:
        return body
    return body + "\n" + _THIRD_PARTY_MANY.format(n=omitted)


def _decode_url(line: str) -> str:
    """Percent-decode until stable (bounded) so encoded separators cannot dodge the mask."""
    for _ in range(_MAX_URL_DECODES):
        decoded = unquote(line)
        if decoded == line:
            break
        line = decoded
    return line


def format_exchange(resp: requests.Response) -> str:
    """Render request line, request content-type, masked request body, status line, selected
    response headers and the masked response body (cut at 2000 chars after masking).

    An empty request body is shown as ``(sem corpo)``.
    """
    request = resp.request
    lines = [mask_text(_decode_url(f"{request.method} {request.url}"))]
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
