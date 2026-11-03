import re
from datetime import date

import pytest

from support.cpf import is_valid_cpf
from support.factory import (
    ACTIVITIES,
    EMPLOYEE_FIELDS,
    EPI_LABELS,
    GENDERS,
    ROLES,
    TEST_PREFIX,
    as_payload,
    build_employee,
)

pytestmark = pytest.mark.unit


def age_in_years(iso_date: str) -> int:
    born = date.fromisoformat(iso_date)
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def test_build_employee_has_exactly_the_expected_fields():
    assert tuple(sorted(build_employee())) == tuple(sorted(EMPLOYEE_FIELDS))


def test_build_employee_produces_valid_synthetic_values():
    emp = build_employee()

    assert emp["name"].startswith(TEST_PREFIX)
    assert emp["cpf"].isdigit()
    assert len(emp["cpf"]) == 11
    assert is_valid_cpf(emp["cpf"])
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", emp["birthDay"])
    assert 18 <= age_in_years(emp["birthDay"]) <= 65
    assert emp["role"] in ROLES
    assert emp["activity"] in ACTIVITIES
    assert emp["epi"] in EPI_LABELS
    assert emp["gender"] in GENDERS
    assert emp["isActive"] is True
    assert emp["usesEpi"] is True
    assert emp["rg"].isdigit()
    assert len(emp["rg"]) == 7
    assert emp["caNumber"].isdigit()
    assert len(emp["caNumber"]) == 5


def test_build_employee_names_differ_between_calls():
    assert build_employee()["name"] != build_employee()["name"]


def test_build_employee_applies_overrides():
    emp = build_employee(isActive=False, role="Cargo 03")

    assert emp["role"] == "Cargo 03"
    assert emp["isActive"] is False


def test_build_employee_rejects_unknown_override_key():
    with pytest.raises(KeyError, match="nmae"):
        build_employee(nmae="x")


def test_epi_labels_has_five_options_with_original_spelling():
    assert len(EPI_LABELS) == 5
    assert "oculor-de-proteçao" in EPI_LABELS


def test_as_payload_wraps_employee_in_state():
    emp = build_employee()

    assert as_payload(emp) == {"state": {"employee": emp}}
