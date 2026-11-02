import pytest
import requests

from support.api_client import EmployeesClient, delete_quietly, describe

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
