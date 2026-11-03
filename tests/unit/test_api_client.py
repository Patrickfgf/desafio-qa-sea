import json

import pytest
import requests
from _pytest.reports import TestReport

from support.api_client import (
    EmployeesClient,
    PreconditionError,
    delete_quietly,
    describe,
    mismatched_fields,
    require_status,
)
from support.pii import mask_report
from tests.conftest import create_employee

pytestmark = pytest.mark.unit


def _json_response(status: int, body) -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp._content = json.dumps(body).encode()
    resp.url = "http://x/employees"
    resp.request = requests.Request("GET", "http://x/employees").prepare()
    return resp


class FakeClient:
    """DELETE answers from ``statuses``; ``?id=`` lookups answer from ``still_listed``."""

    def __init__(self, statuses: dict, still_listed: dict | None = None, list_status: int = 200):
        self._statuses = statuses
        self._still_listed = still_listed or {}
        self._list_status = list_status
        self.list_params: list[dict | None] = []

    def delete(self, employee_id):
        resp = requests.Response()
        resp.status_code = self._statuses[employee_id]
        return resp

    def list(self, params=None):
        self.list_params.append(params)
        employee_id = (params or {}).get("id")
        return _json_response(self._list_status, self._still_listed.get(employee_id, []))


def test_url_for_accepts_int_and_str_ids():
    client = EmployeesClient("http://x")

    assert client.url_for().endswith("/employees")
    assert client.url_for(7).endswith("/employees/7")
    assert client.url_for("a1b2").endswith("/employees/a1b2")
    assert client.url_for("a/b").endswith("/employees/a%2Fb")


def test_delete_quietly_ignores_already_deleted():
    leftovers = delete_quietly(FakeClient({1: 200, 2: 404, 3: 500}), [1, 2, 3])

    assert leftovers == [3]


def test_delete_quietly_confirms_404_by_id_filter():
    client = FakeClient({"a1": 200, "b2": 404})

    delete_quietly(client, ["a1", "b2"])

    assert client.list_params == [{"id": "b2"}]


def test_delete_quietly_flags_404_when_record_is_still_listed():
    # json-server v1 answers 404 on /employees/7 for an int id, yet ?id=7 still finds it.
    client = FakeClient({7: 404}, still_listed={7: [{"id": 7}]})

    assert delete_quietly(client, [7]) == [7]


def test_delete_quietly_flags_404_when_confirmation_fails():
    client = FakeClient({"c3": 404}, list_status=500)

    assert delete_quietly(client, ["c3"]) == ["c3"]


def test_describe_masks_cpf_in_body():
    resp = requests.Response()
    resp.status_code = 201
    resp._content = b'{"cpf":"52998224725"}'
    resp.request = requests.Request("POST", "http://x/employees").prepare()

    text = describe(resp)

    assert "529.***.***-25" in text
    assert "52998224725" not in text


class FakeSession:
    """Answers every GET with ``resp`` and records the query params of each call."""

    def __init__(self, resp: requests.Response):
        self._resp = resp
        self.params: list[dict | None] = []

    def get(self, url, params=None, timeout=None):
        self.params.append(params)
        return self._resp


def _list_client(status: int, body) -> EmployeesClient:
    client = EmployeesClient("http://x")
    client.session = FakeSession(_json_response(status, body))  # type: ignore[assignment]
    return client


def _record(rec_id, name):
    return {"id": rec_id, "state": {"employee": {"name": name}}}


def test_find_ids_by_name_accepts_array_and_wrapped_list():
    records = [_record(1, "a"), _record("x9", "a"), _record(3, "b")]

    assert _list_client(200, records).find_ids_by_name("a") == [1, "x9"]
    assert _list_client(200, {"data": records}).find_ids_by_name("b") == [3]


def test_find_ids_by_name_skips_malformed_records():
    records = [
        None,
        {"id": 1},
        {"id": 2, "state": None},
        {"id": 3, "state": {"employee": 5}},
        _record(4, "a"),
    ]

    assert _list_client(200, records).find_ids_by_name("a") == [4]


def test_find_ids_by_names_filters_on_the_server_one_get_per_name():
    client = _list_client(200, [_record(1, "QA-AUTO-a")])

    client.find_ids_by_names({"QA-AUTO-a"})

    assert client.session.params == [{"state.employee.name": "QA-AUTO-a"}]


def test_find_ids_by_names_keeps_exact_client_side_match():
    # Defence in depth: never trust the server filter to be exact.
    records = [_record(1, "QA-AUTO-a"), _record(2, "QA-AUTO-a-other")]

    assert _list_client(200, records).find_ids_by_names({"QA-AUTO-a"}) == [1]


def test_find_ids_by_name_raises_on_non_200():
    with pytest.raises(PreconditionError, match="500"):
        _list_client(500, {"error": "x"}).find_ids_by_name("a")


def test_mismatched_fields_reports_names_only():
    expected = {"a": "52998224725", "b": 1, "c": 2}
    actual = {"a": "00000000000", "b": 1, "d": 4}

    assert mismatched_fields(expected, actual) == ["a", "c", "d"]
    assert mismatched_fields(expected, dict(expected)) == []


def test_mask_report_masks_failure_text_and_captured_sections():
    report = TestReport(
        nodeid="t::x",
        when="call",
        location=("t", 0, "x"),
        keywords={},
        outcome="failed",
        longrepr="E assert {'cpf': '52998224725'}",
        sections=[("Captured stdout", "52998224725")],
    )

    mask_report(report)

    assert "52998224725" not in str(report.longrepr)
    assert "529.***.***-25" in str(report.longrepr)
    assert report.sections == [("Captured stdout", "529.***.***-25")]


def test_require_status_raises_precondition_error_that_xfail_cannot_swallow():
    with pytest.raises(PreconditionError, match="500") as caught:
        require_status(_json_response(500, {"error": "x"}), 201)

    assert not isinstance(caught.value, AssertionError)


def test_create_employee_with_server_error_raises_precondition_not_assertion():
    class StubApi:
        def create(self, payload):
            return _json_response(500, {"error": "x"})

    ids: list = []
    create = create_employee.__wrapped__(StubApi(), ids)

    with pytest.raises(PreconditionError) as caught:
        create()

    assert not isinstance(caught.value, AssertionError)
