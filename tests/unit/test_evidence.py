import json

import pytest
import requests

from support.evidence import format_exchange, save_exchange

pytestmark = pytest.mark.unit

CPF_RAW = "52998224725"
CPF_MASKED = "529.***.***-25"


def _exchange(
    req_body: bytes | None = b'{"cpf":"52998224725"}',
    resp_body: str = '{"name":"QA-AUTO-x","cpf":"52998224725"}',
    resp_headers: dict | None = None,
    url: str = "http://x/employees",
) -> requests.Response:
    resp = requests.Response()
    resp.status_code = 201
    resp.reason = "Created"
    resp.headers.update(resp_headers or {"Content-Type": "application/json"})
    resp._content = resp_body.encode("utf-8")
    request = requests.Request(
        "POST",
        url,
        headers={"Content-Type": "application/json"},
        data=req_body,
    ).prepare()
    resp.request = request
    return resp


def test_format_exchange_masks_both_bodies():
    text = format_exchange(_exchange())

    assert text.count(CPF_MASKED) == 2
    assert CPF_RAW not in text


def test_format_exchange_includes_cors_header():
    resp = _exchange(resp_headers={"Access-Control-Allow-Origin": "*,*"})

    assert "access-control-allow-origin: *,*" in format_exchange(resp)


def test_format_exchange_follows_documented_order():
    resp = _exchange(resp_headers={"X-Powered-By": "Express", "Content-Type": "text/plain"})

    lines = format_exchange(resp).splitlines()

    assert lines[0] == "POST http://x/employees"
    assert lines[1] == "content-type: application/json"
    assert lines[3] == "HTTP 201 Created"
    assert lines[4] == "content-type: text/plain"
    assert lines[5] == "x-powered-by: Express"


def test_format_exchange_marks_empty_request_body():
    resp = _exchange(req_body=None)

    assert "(sem corpo)" in format_exchange(resp)


def test_format_exchange_ends_with_newline():
    assert format_exchange(_exchange()).endswith("\n")


def test_format_exchange_masks_cpf_before_truncating():
    # CPF straddles the 2000-char boundary: cutting first would leave an unmasked tail.
    body = "a" * 1995 + CPF_RAW + "tail"

    text = format_exchange(_exchange(resp_body=body))

    assert CPF_RAW not in text
    assert CPF_RAW[:6] not in text
    assert "a" * 1995 in text
    assert "tail" not in text


@pytest.mark.parametrize(
    "cpf",
    [CPF_RAW, "x" + CPF_RAW + "y", "529.982.247-25"],
    ids=["bare", "glued", "dotted"],
)
def test_format_exchange_masks_cpf_in_url_and_bodies(cpf):
    resp = _exchange(
        req_body=f'{{"cpf":"{cpf}"}}'.encode(),
        resp_body=f'{{"name":"QA-AUTO-x","cpf":"{cpf}"}}',
        url=f"http://x/employees?state.employee.cpf={cpf}",
    )

    text = format_exchange(resp)

    assert CPF_RAW not in text
    assert "529.982.247-25" not in text
    assert "529.982" not in text
    assert text.splitlines()[0].count("529.***.***-25") == 1


def test_format_exchange_masks_cpf_in_header_value():
    resp = _exchange(resp_headers={"X-Powered-By": CPF_RAW})

    assert CPF_RAW not in format_exchange(resp)


def test_format_exchange_keeps_exactly_2000_chars_of_long_body():
    text = format_exchange(_exchange(resp_body="b" * 2500))

    assert text.splitlines()[-1] == "b" * 2000


def test_format_exchange_skips_absent_optional_headers():
    text = format_exchange(_exchange(resp_headers={"Content-Type": "text/plain"}))

    assert "x-powered-by" not in text
    assert "access-control" not in text


def test_save_exchange_writes_utf8(tmp_path):
    resp = _exchange(resp_body='{"name":"QA-AUTO-João"}')
    path = tmp_path / "nested" / "evidence.txt"

    saved = save_exchange(resp, path)

    assert saved == path
    assert "João" in path.read_text(encoding="utf-8")


# --- ownership rule: third-party records must never reach the evidence file -------------------

OURS = {
    "id": "a1",
    "state": {
        "employee": {
            "name": "QA-AUTO-Maria abc123",
            "cpf": "abcdefghijk",
            "rg": "RG-OURS-1",
            "birthDay": "2023-02-30",
        }
    },
}
STRANGER = {
    "id": "b2",
    "state": {
        "employee": {
            "name": "Joao Estranho Silva",
            "cpf": "11144477735",
            "rg": "RG-STRANGER-9",
            "birthDay": "1980-05-17",
        }
    },
}
STRANGER_LEAKS = ("Joao Estranho", "RG-STRANGER-9", "1980-05-17", "11144477735", "111.444")


def _json_exchange(payload) -> requests.Response:
    return _exchange(resp_body=json.dumps(payload))


def _assert_no_stranger(text: str) -> None:
    for leak in STRANGER_LEAKS:
        assert leak not in text


def test_list_keeps_ours_and_omits_third_party():
    text = format_exchange(_json_exchange([OURS, STRANGER]))

    assert json.dumps(OURS, ensure_ascii=False) in text
    _assert_no_stranger(text)
    assert "(1 registro(s) de terceiros omitido(s) da evidência)" in text


def test_json_server_envelope_omits_third_party():
    text = format_exchange(_json_exchange({"first": 1, "items": 2, "data": [STRANGER, OURS]}))

    assert "QA-AUTO-Maria abc123" in text
    _assert_no_stranger(text)
    assert "1 registro(s) de terceiros omitido(s)" in text


def test_single_third_party_record_becomes_only_omission_text():
    text = format_exchange(_json_exchange(STRANGER))

    _assert_no_stranger(text)
    assert text.splitlines()[-1] == "(registro de terceiro omitido da evidência)"
    assert "registro(s)" not in text


def test_ours_keeps_invalid_values_raw_and_masks_valid_cpf():
    record = {
        "id": "a1",
        "state": {"employee": {"name": "QA-AUTO-X", "cpf": CPF_RAW, "birthDay": "2023-02-30"}},
    }

    text = format_exchange(_json_exchange(record))

    assert CPF_RAW not in text
    assert CPF_MASKED in text
    assert "2023-02-30" in text


@pytest.mark.parametrize("neutral", [{"id": "x"}, {"state": {"employee": {}}}])
def test_neutral_records_are_kept(neutral):
    text = format_exchange(_json_exchange([neutral, STRANGER]))

    assert json.dumps(neutral, ensure_ascii=False) in text
    _assert_no_stranger(text)


def test_non_json_body_is_still_cpf_masked():
    text = format_exchange(_exchange(resp_body=f"plain {CPF_RAW} text"))

    assert CPF_RAW not in text
    assert CPF_MASKED in text


def test_percent_encoded_cpf_in_url_is_masked():
    resp = _exchange(url="http://x/employees?state.employee.cpf=529%2E982%2E247%2D25")

    first_line = format_exchange(resp).splitlines()[0]

    assert "529%2E982" not in first_line
    assert "529.982" not in first_line
    assert "529.***.***-25" in first_line


# --- fail-closed walking: shapes that must not leak a stranger ---------------------------------

T = STRANGER["state"]["employee"]


@pytest.mark.parametrize(
    "payload",
    [
        {"data": STRANGER},
        {"items": [STRANGER]},
        {"result": STRANGER},
        {"result": {"deep": [{"x": STRANGER}]}},
        [[STRANGER]],
        [{"state": {"employee": [T]}}],
        {"state": {"employee": {}}, **T},
        {"state": {"employee": {"name": "QA-AUTO-x"}}, "owner": STRANGER},
        {"state": {"employee": {"name": "QA-AUTO-x"}, "owner": T}},
        {"State": {"Employee": {"Name": "Zed", "CPF": "11144477735", "RG": "RG-STRANGER-9"}}},
        {"Name": "Joao Estranho Silva", "birthday": "1980-05-17", "Rg": "RG-STRANGER-9"},
        {"state": {"employee": T}, "name": "QA-AUTO-x"},
    ],
    ids=[
        "data-dict",
        "items-list",
        "other-wrapper",
        "deep-wrapper",
        "nested-list",
        "employee-list",
        "empty-employee-plus-top-level-pii",
        "sibling-owner",
        "sibling-in-state",
        "mixed-case-keys",
        "mixed-case-bare",
        "ours-name-theirs-employee",
    ],
)
def test_unknown_shapes_never_leak_third_party(payload):
    text = format_exchange(_json_exchange(payload))

    _assert_no_stranger(text)
    assert "Zed" not in text
    assert "omitid" in text.splitlines()[-1]


def test_two_omissions_are_counted_and_all_third_party_list_is_empty():
    text = format_exchange(_json_exchange([STRANGER, STRANGER]))

    _assert_no_stranger(text)
    assert text.splitlines()[-2] == "[]"
    assert text.splitlines()[-1] == "(2 registro(s) de terceiros omitido(s) da evidência)"


def test_bare_unwrapped_third_party_employee_is_omitted():
    text = format_exchange(_json_exchange(T))

    _assert_no_stranger(text)
    assert text.splitlines()[-1] == "(registro de terceiro omitido da evidência)"


def test_double_encoded_json_is_decoded_and_filtered():
    body = json.dumps(json.dumps(STRANGER))

    text = format_exchange(_exchange(resp_body=body))

    _assert_no_stranger(text)
    assert text.splitlines()[-1] == "(registro de terceiro omitido da evidência)"


@pytest.mark.parametrize(
    "body",
    [
        json.dumps(STRANGER) + " trailing garbage",
        json.dumps(STRANGER) + "\n" + json.dumps(STRANGER),
        "error: " + json.dumps(T),
        "name=Joao Estranho Silva&rg=RG-STRANGER-9",
    ],
    ids=["trailing-garbage", "ndjson", "error-echo", "form-encoded"],
)
def test_unparsable_body_with_pii_keys_is_omitted(body):
    text = format_exchange(_exchange(resp_body=body))

    _assert_no_stranger(text)
    assert "omitid" in text.splitlines()[-1]


def test_deeply_nested_json_does_not_crash_or_leak():
    body = "[" * 100000 + json.dumps(T) + "]" * 100000

    text = format_exchange(_exchange(resp_body=body))

    _assert_no_stranger(text)


def test_json_string_body_keeps_its_quotes():
    text = format_exchange(_exchange(resp_body='"hello"'))

    assert text.splitlines()[-1] == '"hello"'


def test_our_record_is_kept_intact_with_odd_values():
    record = {
        "id": "a1",
        "extra": [1, {"k": None}],
        "state": {
            "employee": {
                "name": "QA-AUTO-Odd",
                "cpf": 12345,
                "rg": "",
                "birthDay": "2099-01-01",
            }
        },
    }

    text = format_exchange(_json_exchange([record]))

    assert json.dumps([record], ensure_ascii=False) in text
    assert "omitid" not in text


def test_json_body_is_masked_before_truncating():
    ours = {"name": "QA-AUTO-x", "rg": "p" * 1960, "cpf": CPF_RAW}
    many = [ours] + [STRANGER] * 3

    text = format_exchange(_json_exchange(many))

    assert CPF_RAW not in text
    assert CPF_RAW[:6] not in text
    assert "p" * 1900 in text
    assert text.splitlines()[-1] == "(3 registro(s) de terceiros omitido(s) da evidência)"
    _assert_no_stranger(text)


def test_double_percent_encoded_cpf_in_url_is_masked():
    resp = _exchange(url="http://x/employees?cpf=529%252E982%252E247%252D25")

    first_line = format_exchange(resp).splitlines()[0]

    assert "529.982" not in first_line
    assert "529%252E982" not in first_line
    assert "529.***.***-25" in first_line
