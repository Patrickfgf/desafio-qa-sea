"""Read back a record created through the UI, by exact name (never by listing the base)."""

from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from support.api_client import EmployeesClient, PreconditionError, require_status

SAVE_DEADLINE_SECONDS = 10.0
POLL_SECONDS = 0.5


def find_saved_record(
    api: EmployeesClient,
    name: str,
    *,
    timeout: float = SAVE_DEADLINE_SECONDS,
    poll: float = POLL_SECONDS,
) -> dict:
    """The single stored record whose ``state.employee.name`` is ``name`` (our own record).

    The app's POST can land after the form has already closed (BUG-013), so the exact-name
    filter is polled until exactly one record shows up. ``WebDriverWait`` is used only as a
    deadline-bound polling loop (it accepts any object); nothing sleeps by hand.
    """
    seen = {"count": 0}

    def _exactly_one(_: object) -> list:
        ids = api.find_ids_by_name(name)
        seen["count"] = len(ids)
        return ids if len(ids) == 1 else []

    try:
        ids = WebDriverWait(api, timeout, poll_frequency=poll).until(_exactly_one)
    except TimeoutException:
        raise PreconditionError(
            f"expected exactly 1 record with the test name within {timeout}s, found {seen['count']}"
        ) from None
    resp = api.get(ids[0])
    require_status(resp, 200)
    return resp.json()
