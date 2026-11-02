import json
from pathlib import Path

import pytest
from jsonschema import validate

from support.api_client import describe

pytestmark = pytest.mark.api

SCHEMA = json.loads(
    (Path(__file__).parents[2] / "support" / "schemas" / "employee.json").read_text(
        encoding="utf-8"
    )
)


def test_created_record_matches_schema(api, create_employee):
    created = create_employee()

    resp = api.get(created["id"])

    assert resp.status_code == 200, describe(resp)
    validate(instance=resp.json(), schema=SCHEMA)
