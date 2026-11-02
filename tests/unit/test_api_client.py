import json

import pytest
import requests
from _pytest.reports import TestReport

from support.api_client import EmployeesClient, delete_quietly, describe, mismatched_fields
from support.pii import mask_report

pytestmark = pytest.mark.unit


class FakeClient:
    def __init__(self, statuses: dict):
        self._statuses = statuses

    def delete(self, employee_id):
        resp = requests.Response()
        resp.status_code = self._statuses[employee_id]
        return resp


def test_url_for_accepts_int_and_str_ids():
    client = EmployeesClient("http://x")

    assert client.url_for().endswith("/employees")
    assert client.url_for(7).endswith("/employees/7")
    assert client.url_for("a1b2").endswith("/employees/a1b2")
    assert client.url_for("a/b").endswith("/employees/a%2Fb")


def test_delete_quietly_ignores_already_deleted():
    leftovers = delete_quietly(FakeClient({1: 200, 2: 404, 3: 500}), [1, 2, 3])

    assert leftovers == [3]


def test_describe_masks_cpf_in_body():
    resp = requests.Response()
    resp.status_code = 201
    resp._content = b'{"cpf":"52998224725"}'
    resp.request = requests.Request("POST", "http://x/employees").prepare()

    text = describe(resp)

    assert "529.***.***-25" in text
    assert "52998224725" not in text


def _list_client(status: int, body) -> EmployeesClient:
    resp = requests.Response()
    resp.status_code = status
    resp._content = json.dumps(body).encode()
    resp.url = "http://x/employees"
    resp.request = requests.Request("GET", "http://x/employees").prepare()

    class FakeSession:
        def get(self, *args, **kwargs):
            return resp

    client = EmployeesClient("http://x")
    client.session = FakeSession()
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


def test_find_ids_by_name_raises_on_non_200():
    with pytest.raises(AssertionError, match="500"):
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
