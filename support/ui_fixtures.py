"""UI fixtures: headless Chrome, redacted screenshot on failure, failure-proof cleanup.

Registered as a plugin from the root conftest, so tests/ui and tests/cross share them.
"""

import re
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

from support.api_client import PreconditionError, delete_quietly
from support.factory import TEST_PREFIX
from support.screenshots import redact_page

SCREENSHOT_DIR = Path("reports/screenshots")

phase_report_key = pytest.StashKey[dict[str, pytest.TestReport]]()


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    # Keep each phase's report on the item so the driver fixture can read it in teardown.
    report = yield
    item.stash.setdefault(phase_report_key, {})[report.when] = report
    return report


@pytest.fixture
def driver(request: pytest.FixtureRequest) -> Iterator[WebDriver]:
    yield from _browser(request, network_log=False)


@pytest.fixture
def network_driver(request: pytest.FixtureRequest) -> Iterator[WebDriver]:
    """Same browser as ``driver`` with Chrome's performance log on (event order, no bodies)."""
    yield from _browser(request, network_log=True)


def _browser(request: pytest.FixtureRequest, *, network_log: bool) -> Iterator[WebDriver]:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--lang=pt-BR")
    if network_log:
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        options.set_capability("goog:perfLoggingPrefs", {"enableNetwork": True})
    drv = webdriver.Chrome(options=options)  # Selenium Manager resolves chromedriver
    yield drv
    try:
        if _failed(request.node):
            _save_screenshot(drv, request.node.nodeid)
    finally:
        try:
            drv.quit()
        except WebDriverException as exc:  # a dead browser must not mask the test outcome
            warnings.warn(f"driver.quit() failed: {type(exc).__name__}", stacklevel=1)


@pytest.fixture
def ui_created_names(api) -> Iterator[list[str]]:
    """Names the test is about to create through the UI; matching records are deleted after.

    The name is recorded before saving, so cleanup runs even when the test fails midway.
    One list GET (find_ids_by_names) resolves every name; only exact matches with our prefix
    are deleted.
    """
    names: list[str] = []
    yield names
    ours = {n for n in names if n.startswith(TEST_PREFIX)}
    if not ours:
        return
    try:
        ids = api.find_ids_by_names(ours)
    except (requests.RequestException, PreconditionError, AssertionError, ValueError) as exc:
        warnings.warn(
            f"Cleanup could not list records ({type(exc).__name__}); UI-created data may remain",
            stacklevel=1,
        )
        return
    leftovers = delete_quietly(api, ids)
    if leftovers:
        warnings.warn(f"Cleanup left {len(leftovers)} record(s) behind", stacklevel=1)


def _failed(item: pytest.Item) -> bool:
    reports = item.stash.get(phase_report_key, {})
    return any(rep.failed for when, rep in reports.items() if when in ("setup", "call"))


def _save_screenshot(drv: WebDriver, nodeid: str) -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    name = re.sub(r"[^\w.-]+", "_", nodeid)
    try:
        redact_page(drv)  # third-party personal data must not reach the image
        drv.save_screenshot(str(SCREENSHOT_DIR / f"{name}.png"))
    except Exception as exc:  # noqa: BLE001 - evidence capture must never mask the real failure
        warnings.warn(f"Screenshot skipped: {type(exc).__name__}", stacklevel=1)
