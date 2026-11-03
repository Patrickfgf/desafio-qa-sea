"""Document-level metadata of the SPA shell. Read-only: nothing is created."""

import pytest

from pages.employee_list_page import EmployeeListPage

pytestmark = pytest.mark.ui

VITE_TEMPLATE_TITLE = "Vite + React + TS"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-022: Título da aba é o do template Vite",
)
def test_page_title_identifies_the_app(driver, base_url):
    EmployeeListPage(driver, base_url).open()  # waits for the SPA to render

    title = driver.title.strip()

    assert title, "the page has no title"
    assert title != VITE_TEMPLATE_TITLE, "the page title is the Vite scaffold text"
