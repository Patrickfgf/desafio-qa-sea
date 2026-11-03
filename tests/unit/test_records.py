"""``find_saved_record`` polls with a deadline; a fake client stands in for the API."""

import pytest

from support.api_client import PreconditionError
from support.records import find_saved_record

pytestmark = pytest.mark.unit

_FAST = {"timeout": 0.5, "poll": 0.01}


class _FakeResponse:
    status_code = 200

    def __init__(self, body):
        self._body = body

    def json(self):
        return self._body


class _FakeClient:
    """Returns ``counts[i]`` ids on the i-th lookup (the last value repeats)."""

    def __init__(self, counts):
        self.counts = list(counts)
        self.lookups = 0

    def find_ids_by_name(self, name):
        index = min(self.lookups, len(self.counts) - 1)
        self.lookups += 1
        return list(range(self.counts[index]))

    def get(self, employee_id):
        return _FakeResponse({"id": employee_id, "state": {"employee": {"name": "x"}}})


def test_found_on_first_try():
    client = _FakeClient([1])

    record = find_saved_record(client, "QA-AUTO-x", **_FAST)

    assert record["id"] == 0
    assert client.lookups == 1


def test_found_after_several_tries():
    client = _FakeClient([0, 0, 0, 1])

    record = find_saved_record(client, "QA-AUTO-x", **_FAST)

    assert record["id"] == 0
    assert client.lookups == 4


@pytest.mark.parametrize("count", [0, 2], ids=["none", "duplicate"])
def test_deadline_raises_precondition_error(count):
    client = _FakeClient([count])

    with pytest.raises(PreconditionError, match=rf"found {count}"):
        find_saved_record(client, "QA-AUTO-x", **_FAST)

    assert client.lookups > 1
