"""Shared fixtures: API client and self-cleaning synthetic employees."""

import os
import warnings

import pytest

from support.api_client import BASE_URL_DEFAULT, EmployeesClient, delete_quietly, describe
from support.factory import as_payload, build_employee
from support.pii import mask_report


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
        # Register for cleanup BEFORE asserting, so a failed assert cannot orphan a record.
        try:
            body = resp.json()
        except ValueError:
            body = None
        if isinstance(body, dict) and "id" in body:
            created_ids.append(body["id"])
        assert resp.status_code == 201, describe(resp)
        return body

    return _create


@pytest.hookimpl(hookwrapper=True, trylast=True)
def pytest_runtest_makereport(item, call):
    """Defense in depth: mask CPFs in failure text and captured output (terminal and HTML)."""
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        mask_report(report)
