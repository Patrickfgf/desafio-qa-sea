"""Form buttons and listing refresh behaviour.

Tests that fill the form register the name in ``ui_created_names`` BEFORE the action that may
create a record. Tests that never submit create nothing.
"""

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from pages.employee_list_page import EmployeeListPage
from support.factory import build_employee
from support.network_log import NetEvent, drain_employee_events, refetch_follows_post_response

pytestmark = pytest.mark.ui

NETWORK_WAIT_SECONDS = 8


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-012: Adicionar outra atividade salva e fecha o formulário",
)
def test_add_another_activity_does_not_submit(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True)
    ui_created_names.append(emp["name"])
    form = EmployeeListPage(driver, base_url).open().click_add().fill(emp)

    form.click_add_activity()
    closed = form.wait_until_closed()

    assert not closed, "form closed after clicking 'Adicionar outra atividade'"
    assert not api.find_ids_by_name(emp["name"]), "the button created a record"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-013: Listagem busca dados em paralelo ao POST e fica velha",
)
def test_listing_refetch_happens_after_post_completes(network_driver, base_url, ui_created_names):
    emp = build_employee(isActive=True)
    ui_created_names.append(emp["name"])
    pending: dict[str, str] = {}
    events: list[NetEvent] = []
    page = EmployeeListPage(network_driver, base_url).open()
    drain_employee_events(network_driver, pending)  # drop the page-load traffic
    form = page.click_add().fill(emp)

    form.submit()

    def settled(_) -> bool:
        events.extend(drain_employee_events(network_driver, pending))
        post_answered = NetEvent("RESP", "POST") in events
        return post_answered and (
            refetch_follows_post_response(events) or form.wait_until_closed(0.5)
        )

    try:
        WebDriverWait(network_driver, NETWORK_WAIT_SECONDS).until(settled)
    except TimeoutException:
        pass
    events.extend(drain_employee_events(network_driver, pending))

    assert NetEvent("RESP", "POST") in events, "no POST response was observed"
    assert refetch_follows_post_response(events), (
        f"no listing GET was sent after the POST response; /employees events: "
        f"{[f'{e.kind} {e.method}' for e in events]}"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-016: Select de EPI volta ao padrão ao digitar o CA",
)
def test_epi_select_keeps_choice_after_typing_ca(driver, base_url):
    form = EmployeeListPage(driver, base_url).open().click_add()
    form.choose_epi("Luvas descartáveis")  # nothing is saved in this test

    form.fill_ca_number("12345")

    shown = form.selected_text("epi")
    assert shown == "Luvas descartáveis", f"EPI select shows {shown!r} after typing the CA"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-017: Adicionar EPI não tem ação nem foco por teclado",
)
def test_add_epi_adds_another_epi_block(driver, base_url):
    form = EmployeeListPage(driver, base_url).open().click_add()
    before = form.epi_select_count()

    form.click_add_epi()

    assert form.wait_for_epi_select_count_above(before), (
        f"EPI select count stayed at {form.epi_select_count()} (was {before})"
    )
