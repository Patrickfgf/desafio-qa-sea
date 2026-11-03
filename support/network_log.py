"""Order of /employees network events, read from Chrome's performance log (no bodies)."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import NamedTuple
from urllib.parse import urlparse

from selenium.webdriver.remote.webdriver import WebDriver

_EMPLOYEES_PATH = "/employees"


class NetEvent(NamedTuple):
    kind: str  # "SEND" (requestWillBeSent) or "RESP" (responseReceived)
    method: str


def drain_employee_events(driver: WebDriver, pending: dict[str, str]) -> list[NetEvent]:
    """Drain the performance log; keep only ``/employees`` traffic, in log order.

    ``pending`` maps requestId -> method across calls, so a response is tied to its request even
    when the two arrive in different drains.
    """
    events: list[NetEvent] = []
    for entry in driver.get_log("performance"):
        message = json.loads(entry["message"])["message"]
        params = message.get("params", {})
        if message["method"] == "Network.requestWillBeSent":
            request = params["request"]
            if urlparse(request["url"]).path == _EMPLOYEES_PATH:
                pending[params["requestId"]] = request["method"]
                events.append(NetEvent("SEND", request["method"]))
        elif message["method"] == "Network.responseReceived" and params["requestId"] in pending:
            events.append(NetEvent("RESP", pending[params["requestId"]]))
    return events


def refetch_follows_post_response(events: Iterable[NetEvent]) -> bool:
    """True when a GET is sent after the POST's response arrived (listing refetch after save)."""
    post_answered = False
    for event in events:
        if event == NetEvent("RESP", "POST"):
            post_answered = True
        elif post_answered and event == NetEvent("SEND", "GET"):
            return True
    return False
