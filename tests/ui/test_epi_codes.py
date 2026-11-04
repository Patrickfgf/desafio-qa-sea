"""Stored EPI codes: what the form writes when each option is chosen.

Every name is registered in ``ui_created_names`` BEFORE saving, so cleanup runs on any outcome.
Messages carry the option label and the stored code only (a catalogue value, not personal data).
"""

import re

import pytest

from pages.employee_list_page import EmployeeListPage
from support.factory import EPI_LABELS, build_employee
from support.records import find_saved_record

pytestmark = pytest.mark.ui

ASCII_SLUG = re.compile(r"^[a-z0-9-]+$")
# Prefix a correct slug of the label would have (the stored code starts with the typo "oculor").
EXPECTED_PREFIX = {"Óculos de proteção": "oculos-"}
BUG_029 = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-029: Códigos de EPI gravados com grafia e acentuação inconsistentes",
)
# Only the options whose stored code breaks the rule are xfail; the other two are the control
# showing the rule is reachable (a strict xfail on them would XPASS and fail the run).
_DEFECTIVE = {"capacete-de-segurança", "oculor-de-proteçao", "calçado-de-segurança"}
_CASES = [
    pytest.param(code, label, marks=BUG_029 if code in _DEFECTIVE else (), id=label)
    for code, label in EPI_LABELS.items()
]


@pytest.mark.parametrize(("code", "label"), _CASES)
def test_saved_epi_code_is_an_ascii_slug(driver, base_url, api, ui_created_names, code, label):
    emp = build_employee(isActive=True, usesEpi=True, epi=code)
    ui_created_names.append(emp["name"])
    form = EmployeeListPage(driver, base_url).open().click_add()
    form.fill_identity(emp)
    form.choose_role(emp["role"])
    form.set_no_epi(False)
    form.choose_activity(emp["activity"])
    if code == "capacete-de-segurança":
        # The select already displays this option, and clicking it again saves nothing (BUG-006).
        form.choose_epi(EPI_LABELS["luvas-descartaveis"])
    form.choose_epi(label)
    form.fill_ca_number(emp["caNumber"])

    form.submit()
    stored = find_saved_record(api, emp["name"])["state"]["employee"].get("epi") or ""

    assert ASCII_SLUG.fullmatch(stored), f"{label!r} was stored as {stored!r}, not an ASCII slug"
    prefix = EXPECTED_PREFIX.get(label)
    assert prefix is None or stored.startswith(prefix), (
        f"{label!r} was stored as {stored!r}, expected a code starting with {prefix!r}"
    )
