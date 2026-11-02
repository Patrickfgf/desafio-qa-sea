"""Shared fixtures: API client and self-cleaning synthetic employees."""

import os
import warnings

import pytest

from support.api_client import BASE_URL_DEFAULT, EmployeesClient, delete_quietly, describe
from support.factory import as_payload, build_employee


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("APP_BASE_URL", BASE_URL_DEFAULT)


@pytest.fixture(scope="session")
def api(base_url) -> EmployeesClient:
    return EmployeesClient(base_url)


@pytest.fixture
def created_ids(api):
    """Ids created by the test; deleted on teardown. Leftovers only warn, never fail."""
    ids: list = []
    yield ids
    leftovers = delete_quietly(api, ids)
    if leftovers:
        warnings.warn(
            f"Cleanup left {len(leftovers)} record(s) behind, ids: {leftovers}", stacklevel=1
        )


@pytest.fixture
def create_employee(api, created_ids):
    """Callable ``(**overrides) -> created JSON``; registers the id for cleanup."""

    def _create(**overrides) -> dict:
        resp = api.create(as_payload(build_employee(**overrides)))
        assert resp.status_code == 201, describe(resp)
        body = resp.json()
        created_ids.append(body["id"])
        return body

    return _create
