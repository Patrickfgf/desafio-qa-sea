"""UI fixtures: headless Chrome, redacted screenshot on failure, failure-proof cleanup."""

import re
import warnings
from collections.abc import Iterator
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from support.api_client import delete_quietly
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
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--lang=pt-BR")
    drv = webdriver.Chrome(options=options)  # Selenium Manager resolves chromedriver
    yield drv
    try:
        if _failed(request.node):
            _save_screenshot(drv, request.node.nodeid)
    finally:
        drv.quit()


@pytest.fixture
def ui_created_names(api) -> Iterator[list[str]]:
    """Names the test is about to create through the UI; matching records are deleted after.

    The name is recorded before saving, so cleanup runs even when the test fails midway.
    One list GET resolves every name; only exact name matches with our prefix are deleted.
    """
    names: list[str] = []
    yield names
    ours = {n for n in names if n.startswith(TEST_PREFIX)}
    if not ours:
        return
    resp = api.list()
    if resp.status_code != 200:
        warnings.warn("Cleanup could not list records; UI-created data may remain", stacklevel=1)
        return
    body = resp.json()
    records = body.get("data", []) if isinstance(body, dict) else body
    ids = [
        rec["id"]
        for rec in records
        if isinstance(rec, dict)
        and "id" in rec
        and ((rec.get("state") or {}).get("employee") or {}).get("name") in ours
    ]
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
