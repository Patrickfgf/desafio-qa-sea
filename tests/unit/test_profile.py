import json
from datetime import date, timedelta

import pytest

from scripts.profile_dataset import main, profile
from support.api_client import EmployeesClient
from support.cpf import is_valid_cpf
from support.factory import as_payload, build_employee
from support.pii import find_unmasked_cpfs

pytestmark = pytest.mark.unit

TODAY = date(2026, 1, 15)


def _break_check_digit(cpf: str) -> str:
    last = "0" if cpf[-1] != "0" else "1"
    return cpf[:-1] + last


def _records():
    shared = build_employee(role="Cargo 01")
    dup = build_employee(
        cpf=shared["cpf"], role="Cargo 01", usesEpi=False, caNumber="12345", isActive=False
    )
    bad_cpf = _break_check_digit(build_employee()["cpf"])
    future = build_employee(
        cpf=bad_cpf,
        role="Cargo 02",
        birthDay=(TODAY + timedelta(days=1)).isoformat(),
    )
    no_ca = build_employee(usesEpi=True, caNumber="", role="Cargo 02")
    employees = [shared, dup, future, no_ca]
    ids = ["a", "b", 3, "d"]
    records = [{"id": i, **as_payload(e)} for i, e in zip(ids, employees, strict=True)]
    return records, employees


def test_profile_reports_exact_aggregates_without_pii():
    records, employees = _records()
    assert not is_valid_cpf(employees[2]["cpf"])

    result = profile(records, TODAY)

    assert result["total"] == 4
    assert result["id_types"] == {"str": 3, "int": 1}
    assert result["employee_key_sets"] == [[sorted(employees[0]), 4]]
    assert result["invalid_cpf"] == 1
    assert result["duplicate_cpf"] == 1
    assert result["future_birthdays"] == 1
    assert result["uses_epi_without_ca"] == 1
    assert result["no_epi_with_ca"] == 1
    assert result["is_active"] == {"true": 3, "false": 1}
    assert result["roles"] == [["Cargo 01", 2], ["Cargo 02", 2]]
    assert result["test_prefixed"] == 4

    dumped = json.dumps(result)
    assert find_unmasked_cpfs(dumped) == []
    assert not [e["name"] for e in employees if e["name"] in dumped]


def test_profile_tolerates_malformed_third_party_records():
    records = [
        None,
        "x",
        {"id": 1},
        {"id": 2, "state": "oops"},
        {"id": 3, "state": {"employee": {"cpf": 123, "birthDay": "not-a-date", "name": 5}}},
        {"id": 4, "state": {"employee": {"cpf": ""}}},
        {"id": 5, "state": {"employee": {"cpf": "abc"}}},
        {"id": 6, "state": {"employee": {"cpf": "²"}}},
    ]

    result = profile(records, TODAY)

    assert result["total"] == 8
    assert result["invalid_cpf"] == 8
    assert result["future_birthdays"] == 0
    assert result["test_prefixed"] == 0


def test_profile_replaces_free_text_outside_the_allowlist():
    name = "Maria Aparecida Souza"
    employee = build_employee(role=name, activity=name, epi=name, caNumber="", isActive=name)
    employee[name] = "x"
    record = as_payload(employee)
    record["state"]["employee"].pop("gender")
    clean = as_payload(build_employee(role="Cargo 01", activity="", epi="protetor-auditivo"))

    result = profile([record, clean], TODAY)

    dumped = json.dumps(result)
    assert "Maria" not in dumped
    assert "Souza" not in dumped
    assert ["<other>", 1] in result["roles"]
    assert ["Cargo 01", 1] in result["roles"]
    assert ["<other>", 1] in result["activities"]
    assert ["", 1] in result["activities"]
    assert ["<other>", 1] in result["epis"]
    assert ["protetor-auditivo", 1] in result["epis"]
    assert result["is_active"] == {"<other>": 1, "true": 1}
    assert any("<unknown>" in keys for keys, _ in result["employee_key_sets"])


def test_profile_masks_missing_and_cpf_like_grouped_values():
    record = as_payload(build_employee(role="12345678909"))
    del record["state"]["employee"]["activity"]

    result = profile([record], TODAY)

    assert find_unmasked_cpfs(json.dumps(result)) == []
    assert result["roles"] == [["<other>", 1]]
    assert result["activities"] == [["missing", 1]]


@pytest.mark.parametrize("payload", [{"foo": 1}, {"data": "x"}, "x", None])
def test_main_rejects_unexpected_list_payload(payload, monkeypatch):
    class Resp:
        status_code = 200

        def json(self):
            return payload

    monkeypatch.setattr(EmployeesClient, "list", lambda self, params=None: Resp())

    with pytest.raises(RuntimeError, match="shape"):
        main()
