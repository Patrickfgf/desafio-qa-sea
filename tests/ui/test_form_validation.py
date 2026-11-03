"""Form validation in the browser: what the form blocks and what it lets through.

Every name is registered in ``ui_created_names`` BEFORE the form is submitted, so a record the
app wrongly accepts is still deleted. Messages carry counts and field names only.
"""

import re

import pytest

from pages.employee_list_page import EmployeeListPage
from support.api_client import EmployeesClient
from support.factory import build_employee
from support.records import find_saved_record

pytestmark = pytest.mark.ui


def _format_cpf(digits: str) -> str:
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def _open_filled_form(driver, base_url, emp):
    return EmployeeListPage(driver, base_url).open().click_add().fill(emp)


def _assert_nothing_stored(api: EmployeesClient, name: str) -> None:
    stored = len(api.find_ids_by_name(name))
    assert stored == 0, f"{stored} record(s) were created by a blocked submit"


def test_cpf_shorter_than_11_blocks_submit(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True)
    ui_created_names.append(emp["name"])
    form = _open_filled_form(driver, base_url, {**emp, "cpf": emp["cpf"][:10]})

    form.submit()

    valid, message = form.field_validity("cpf")
    assert not valid, "a 10-digit CPF passed native validation"
    assert message, "no native validation message for the short CPF"
    assert form.is_open(), "form closed with a 10-digit CPF"
    _assert_nothing_stored(api, emp["name"])


def test_empty_ca_blocks_submit_with_native_message(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True, usesEpi=True)
    ui_created_names.append(emp["name"])
    form = EmployeeListPage(driver, base_url).open().click_add()
    form.set_active(True)
    form.fill_identity(emp)
    form.choose_role(emp["role"])  # EPI checkbox unticked, CA number left empty

    form.submit()

    valid, message = form.field_validity("caNumber")
    assert not valid, "empty CA number passed native validation"
    assert message, "no native validation message for the empty CA number"
    assert form.is_open(), "form closed with an empty CA number"
    _assert_nothing_stored(api, emp["name"])


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-008: CPF aceito sem validação de conteúdo",
)
def test_cpf_field_rejects_letters(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True, cpf="abcdefghijk")
    ui_created_names.append(emp["name"])
    form = _open_filled_form(driver, base_url, emp)

    form.submit()

    if not form.wait_until_closed():
        return  # blocked before saving: the accepted behaviour
    # A closed form proves nothing (BUG-024, API errors): judge the stored value, and treat
    # "nothing saved" as a broken precondition, not as the bug.
    stored = find_saved_record(api, emp["name"])["state"]["employee"]["cpf"]
    assert stored != "abcdefghijk", "a CPF made of letters was stored as typed"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-009: CPF digitado com máscara é truncado sem aviso",
)
def test_formatted_cpf_is_not_silently_truncated(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True)
    ui_created_names.append(emp["name"])
    form = _open_filled_form(driver, base_url, emp)
    form.type_cpf_by_key(_format_cpf(emp["cpf"]))

    form.submit()

    if not form.wait_until_closed():
        return  # the app refused the input (a message is the accepted alternative)
    stored = find_saved_record(api, emp["name"])["state"]["employee"]["cpf"]
    kept = len(re.sub(r"\D", "", stored))
    assert kept == len(emp["cpf"]), f"stored CPF kept {kept} of {len(emp['cpf'])} digits"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-010: Data de nascimento sem validação de intervalo",
)
def test_birth_date_rejects_future(driver, base_url, api, ui_created_names):
    emp = build_employee(isActive=True, birthDay="2099-12-31")
    ui_created_names.append(emp["name"])
    form = _open_filled_form(driver, base_url, emp)

    form.submit()

    if not form.wait_until_closed():
        return  # blocked before saving: the accepted behaviour
    stored = find_saved_record(api, emp["name"])["state"]["employee"]["birthDay"]
    assert stored != "2099-12-31", "a birth date in 2099 was stored as typed"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-023: Obrigatórios aceitam só espaços",
)
@pytest.mark.parametrize(
    ("field", "blank"),
    [("rg", " " * 3), ("caNumber", " " * 3), ("cpf", " " * 11)],
    ids=["rg", "ca-number", "cpf"],
)
def test_required_fields_reject_whitespace_only(
    driver, base_url, api, ui_created_names, field, blank
):
    emp = build_employee(isActive=True, usesEpi=True, **{field: blank})
    ui_created_names.append(emp["name"])
    form = _open_filled_form(driver, base_url, emp)

    form.submit()

    if not form.wait_until_closed():
        return  # blocked before submit: the accepted behaviour
    stored = find_saved_record(api, emp["name"])["state"]["employee"].get(field) or ""
    assert stored.strip(), f"{field} was saved as whitespace only (length {len(stored)})"
