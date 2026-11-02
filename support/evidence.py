"""HTTP evidence helpers: a masked, bounded text record of one request/response exchange.

Bodies are masked with ``mask_text`` BEFORE truncation, so a CPF cut at the boundary can never
leak an unmasked partial tail.
"""

from pathlib import Path

import requests

from support.pii import mask_text

MAX_RESPONSE_BODY_CHARS = 2000
EMPTY_BODY_MARKER = "(sem corpo)"
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
    return [f"{name}: {headers[name]}" for name in names if name in headers]


def format_exchange(resp: requests.Response) -> str:
    """Render request line, request content-type, masked request body, status line, selected
    response headers and the masked response body (cut at 2000 chars after masking).

    An empty request body is shown as ``(sem corpo)``.
    """
    request = resp.request
    lines = [f"{request.method} {request.url}"]
    lines += _header_lines(request.headers, _REQUEST_HEADERS)
    lines.append(_masked_request_body(resp))
    lines.append(f"HTTP {resp.status_code} {resp.reason}")
    lines += _header_lines(resp.headers, _RESPONSE_HEADERS)
    lines.append(mask_text(resp.text)[:MAX_RESPONSE_BODY_CHARS])
    return "\n".join(lines) + "\n"


def save_exchange(resp: requests.Response, path: Path) -> Path:
    """Write ``format_exchange(resp)`` to ``path`` (utf-8), creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_exchange(resp), encoding="utf-8")
    return path
