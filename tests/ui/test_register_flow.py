"""UI happy path: register an active employee through the form and find it in the listing."""

import pytest

from pages.employee_list_page import EmployeeListPage
from support.factory import build_employee


@pytest.mark.ui
def test_register_active_employee_appears_in_list(
    driver, base_url, api, created_ids, ui_created_names
):
    emp = build_employee(isActive=True)
    ui_created_names.append(emp["name"])  # recorded BEFORE saving so cleanup survives failures

    listing = EmployeeListPage(driver, base_url).open().click_add().fill(emp).save()
    assert listing is not None
    # The app does not refresh the listing after saving, so re-open it to read persisted data.
    card = EmployeeListPage(driver, base_url).open().wait_for_card(emp["name"])

    assert card.role == emp["role"]
    assert card.activity == emp["activity"]
