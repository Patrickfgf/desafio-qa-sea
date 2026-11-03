"""Cross-checks between what the UI shows/sends and what the API stores.

Bug tests are strict xfails (all still "pending manual reproduction", DEC-14); the rest pass.
Every UI-created name is registered in ``ui_created_names`` BEFORE saving.
"""

import json
import re
from uuid import uuid4

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.employee_list_page import EmployeeListPage
from support.api_client import mismatched_fields
from support.factory import TEST_PREFIX, build_employee
from support.records import find_saved_record

pytestmark = pytest.mark.cross

COMPARED_FIELDS = (
    "name",
    "gender",
    "cpf",
    "birthDay",
    "rg",
    "role",
    "activity",
    "epi",
    "caNumber",
    "isActive",
)  # usesEpi is left out on purpose: it has its own test (BUG-001)


def _employee_of(record: dict) -> dict:
    return record["state"]["employee"]


def test_ui_saved_fields_match_api_record(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True)
    ui_created_names.append(emp["name"])

    EmployeeListPage(driver, base_url).open().click_add().fill(emp).save()
    stored = _employee_of(find_saved_record(api, emp["name"]))

    expected = {k: emp[k] for k in COMPARED_FIELDS}
    actual = {k: stored.get(k) for k in COMPARED_FIELDS}
    # Field names only: a dict diff would print the CPF.
    assert not mismatched_fields(expected, actual), (
        f"UI-saved fields differ from the API record: {mismatched_fields(expected, actual)}"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-001: Checkbox não usa EPI grava usesEpi invertido",
)
@pytest.mark.parametrize("uses_epi", [True, False])
def test_uses_epi_flag_matches_checkbox(driver, base_url, api, ui_created_names, uses_epi):
    # The checkbox means "does NOT use EPI": unticked <=> usesEpi=True.
    emp = build_employee(isActive=True, usesEpi=uses_epi)
    ui_created_names.append(emp["name"])

    EmployeeListPage(driver, base_url).open().click_add().fill(emp).save()
    stored = _employee_of(find_saved_record(api, emp["name"]))

    assert stored.get("usesEpi") is uses_epi, (
        f"checkbox state implies usesEpi={uses_epi}, API stored {stored.get('usesEpi')!r}"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-006: Selects exibem padrão que não é gravado ao salvar",
)
def test_default_selects_are_saved_as_displayed(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True, usesEpi=True)
    ui_created_names.append(emp["name"])

    form = EmployeeListPage(driver, base_url).open().click_add()
    form.set_active(True)
    form.fill_identity(emp)
    form.fill_ca_number(emp["caNumber"])  # role, activity and EPI selects are left untouched
    form.save()
    stored = _employee_of(find_saved_record(api, emp["name"]))

    expected = {"role": "Cargo 01", "activity": "Ativid 01", "epi": "capacete-de-segurança"}
    actual = {k: stored.get(k) for k in expected}
    assert not mismatched_fields(expected, actual), (
        f"displayed defaults not stored for: {mismatched_fields(expected, actual)}"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-007: Anexo do ASO não é enviado nem persistido",
)
def test_aso_file_is_persisted(driver, base_url, api, ui_created_names, tmp_path):
    aso = tmp_path / "aso.pdf"
    aso.write_bytes(b"%PDF-1.4 QA-AUTO synthetic file\n")
    emp = build_employee(isActive=True)
    ui_created_names.append(emp["name"])

    form = EmployeeListPage(driver, base_url).open().click_add().fill(emp)
    form.attach_aso(aso)
    form.save()
    record = find_saved_record(api, emp["name"])

    # The faker name could contain "aso" by chance, so the name is dropped before searching.
    without_name = {**_employee_of(record), "name": ""}
    keys = set(record) | set(without_name) | set(record.get("state", {}))
    text = json.dumps({**record, "state": {"employee": without_name}}).lower()
    has_reference = "aso.pdf" in text or any(
        re.search(r"aso|file|anexo|attach", key.lower()) for key in keys
    )
    assert has_reference, (
        f"stored record has no reference to the attached file; keys: {sorted(keys)}"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-003: Listagem exibe o CPF completo no card",
)
def test_listing_card_masks_cpf(driver, base_url, create_employee):
    created = create_employee()
    employee = _employee_of(created)

    card = EmployeeListPage(driver, base_url).open().wait_for_card(employee["name"])

    is_masked = "*" in card.cpf
    shows_full_cpf = re.sub(r"\D", "", card.cpf) == employee["cpf"]
    assert is_masked, "card CPF has no mask character"
    assert not shows_full_cpf, "card shows all 11 CPF digits"


def test_api_created_employee_appears_in_list(driver, base_url, create_employee):
    employee = _employee_of(create_employee())

    card = EmployeeListPage(driver, base_url).open().wait_for_card(employee["name"])

    assert card.name == employee["name"]
    assert card.role == employee["role"]
    assert card.activity == employee["activity"]


def test_inactive_employee_hidden_with_active_filter(driver, base_url, create_employee):
    inactive = _employee_of(create_employee(isActive=False))
    active = _employee_of(create_employee(isActive=True))

    page = EmployeeListPage(driver, base_url).open()
    page.wait_for_card(inactive["name"])
    page.wait_for_card(active["name"])
    page.toggle_active_only()
    WebDriverWait(driver, 10).until(lambda _: page.find_card(inactive["name"]) is None)

    assert page.find_card(active["name"]) is not None, "active employee vanished under the filter"


def test_listing_renders_name_markup_as_text(driver, base_url, create_employee):
    # Inert markup (allowed by the plan): the card must show it literally, not interpret it.
    token = uuid4().hex[:8]
    name = f"{TEST_PREFIX}markup-{token}-<b>qa</b>"
    create_employee(name=name)
    EmployeeListPage(driver, base_url).open()
    # Only our card: the token is unique to this run, so no one else's record can match.
    name_span = (By.XPATH, f"//span[contains(text(), '{token}')]")

    span = WebDriverWait(driver, 10).until(lambda d: d.find_element(*name_span))

    assert span.get_attribute("textContent").strip() == name, "card does not show the literal name"
    assert not span.find_elements(By.TAG_NAME, "b"), "card rendered the name as HTML (<b> element)"
