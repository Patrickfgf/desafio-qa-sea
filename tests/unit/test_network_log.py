import pytest

from support.network_log import NetEvent, refetch_follows_post_response

SEND_GET = NetEvent("SEND", "GET")
SEND_POST = NetEvent("SEND", "POST")
RESP_POST = NetEvent("RESP", "POST")
RESP_GET = NetEvent("RESP", "GET")


@pytest.mark.unit
@pytest.mark.parametrize(
    ("events", "expected"),
    [
        ([SEND_POST, RESP_POST, SEND_GET], True),
        ([SEND_POST, SEND_GET, RESP_POST], False),  # GET leaves in parallel with the POST
        ([SEND_GET, RESP_GET, SEND_POST, RESP_POST], False),  # only a GET from before the POST
        ([SEND_POST, RESP_POST], False),
        ([], False),
    ],
)
def test_refetch_follows_post_response(events, expected):
    assert refetch_follows_post_response(events) is expected
