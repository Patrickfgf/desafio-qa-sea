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
        resp_body=f'{{"cpf":"{cpf}"}}',
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
    import json

    return _exchange(resp_body=json.dumps(payload), url="http://x/employees")


def _assert_no_stranger(text: str) -> None:
    for leak in STRANGER_LEAKS:
        assert leak not in text


def test_list_keeps_ours_and_omits_third_party():
    text = format_exchange(_json_exchange([OURS, STRANGER]))

    assert "QA-AUTO-Maria abc123" in text
    assert "abcdefghijk" in text
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
    assert "state" not in text.split("HTTP 201 Created", 1)[1]
    assert "(registro de terceiro omitido da evidência)" in text


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

    assert json_fragment(neutral) in text
    _assert_no_stranger(text)


def json_fragment(neutral: dict) -> str:
    import json

    return json.dumps(neutral, ensure_ascii=False)


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
