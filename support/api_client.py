"""Thin client for the /employees REST API (json-server v1) plus safe response formatting."""

from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import quote

import requests

from support.pii import mask_text

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
        """One GET of the list, filtered client-side (never loops over the shared base)."""
        records = self.list().json()
        return [
            r["id"] for r in records if r.get("state", {}).get("employee", {}).get("name") == name
        ]


def describe(resp: requests.Response) -> str:
    """``METHOD url -> status: body``; the body is masked BEFORE truncation (no partial CPF)."""
    request = resp.request
    method = request.method if request is not None else "?"
    url = resp.url or (request.url if request is not None else "?")
    body = mask_text(resp.text)[:DESCRIBE_MAX_CHARS]
    return f"{method} {url} -> {resp.status_code}: {body}"


def delete_quietly(client, ids: Iterable[EmployeeId]) -> list[EmployeeId]:
    """Delete each id; return those whose DELETE was not 200/204/404 (or raised)."""
    leftovers = []
    for employee_id in ids:
        try:
            status = client.delete(employee_id).status_code
        except requests.RequestException:
            leftovers.append(employee_id)
            continue
        if status not in _ALREADY_GONE:
            leftovers.append(employee_id)
    return leftovers
