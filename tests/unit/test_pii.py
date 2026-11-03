import copy

import pytest

from support.pii import (
    find_unmasked_cpfs,
    mask_birth_date,
    mask_cpf,
    mask_employee,
    mask_name,
    mask_rg,
    mask_text,
    scan_tree,
)

pytestmark = pytest.mark.unit


def test_mask_cpf_keeps_first_three_and_last_two_digits():
    assert mask_cpf("52998224725") == "529.***.***-25"
    assert mask_cpf("529.982.247-25") == "529.***.***-25"


def test_mask_cpf_masks_everything_when_not_a_full_cpf():
    assert mask_cpf("1234") == "****"


def test_mask_rg_keeps_last_two_characters():
    assert mask_rg("1234567") == "*****67"
    assert mask_rg("12") == "**"


def test_mask_name_keeps_first_letter_of_each_word():
    assert mask_name("Maria da Silva") == "M**** d* S****"


def test_mask_birth_date_keeps_only_the_year_of_iso_dates():
    assert mask_birth_date("1990-05-17") == "1990-**-**"


def test_mask_birth_date_masks_everything_when_not_iso():
    assert mask_birth_date("17/05/1990") == "**********"


def test_mask_employee_masks_four_fields_and_does_not_mutate_input():
    record = {
        "id": "ab12",
        "state": {
            "employee": {
                "name": "Maria Silva",
                "cpf": "52998224725",
                "rg": "1234567",
                "birthDay": "1990-05-17",
                "role": "Cargo 01",
            }
        },
    }
    original = copy.deepcopy(record)

    masked = mask_employee(record)

    assert masked["state"]["employee"] == {
        "name": "M**** S****",
        "cpf": "529.***.***-25",
        "rg": "*****67",
        "birthDay": "1990-**-**",
        "role": "Cargo 01",
    }
    assert record == original


def test_mask_employee_tolerates_missing_keys():
    assert mask_employee({"id": 1}) == {"id": 1}


def test_find_unmasked_cpfs_ignores_masked_and_timestamps():
    text = "a 529.982.247-25 b 52998224725 c 529.***.***-25 d 1730000000000"
    assert find_unmasked_cpfs(text) == ["529.982.247-25", "52998224725"]


def test_mask_text_replaces_each_unmasked_cpf():
    assert mask_text("cpf=52998224725;") == "cpf=529.***.***-25;"


def test_scan_tree_counts_cpfs_only_in_matching_suffixes(tmp_path):
    (tmp_path / "a.md").write_text("cpf 529.982.247-25", encoding="utf-8")
    (tmp_path / "b.txt").write_text("clean", encoding="utf-8")
    (tmp_path / "c.png").write_text("52998224725", encoding="utf-8")

    assert scan_tree(tmp_path) == {"a.md": 1}


def test_find_unmasked_cpfs_finds_cpfs_glued_to_letters():
    assert find_unmasked_cpfs("user_52998224725 x") == ["52998224725"]
    assert find_unmasked_cpfs("id529.982.247-25") == ["529.982.247-25"]


def test_find_unmasked_cpfs_ignores_longer_digit_runs():
    assert find_unmasked_cpfs("1234567890123") == []


def test_mask_text_masks_cpf_glued_to_letters():
    assert mask_text("id529.982.247-25") == "id529.***.***-25"
    assert mask_text("user_52998224725") == "user_529.***.***-25"


def test_mask_employee_masks_non_string_values():
    record = {"state": {"employee": {"cpf": 52998224725, "rg": 1234567, "name": None}}}

    employee = mask_employee(record)["state"]["employee"]

    assert employee == {"cpf": "529.***.***-25", "rg": "*****67", "name": None}


def test_find_unmasked_cpfs_catches_dash_and_slash_variants():
    text = "a 123456789-09 b 123.456.789/09 c 123456789/09 d 123.456789-09"
    assert find_unmasked_cpfs(text) == [
        "123456789-09",
        "123.456.789/09",
        "123456789/09",
        "123.456789-09",
    ]


def test_mask_text_masks_dash_and_slash_variants():
    assert mask_text("x 123456789-09 y 123.456.789/09") == "x 123.***.***-09 y 123.***.***-09"


def test_find_unmasked_cpfs_ignores_ordinary_numbers():
    text = "ip 192.168.100.12 date 2026-11-03 part 123.456.789 ts 1730000000-09 v 12.345.678/0001"
    assert find_unmasked_cpfs(text) == []


def test_find_unmasked_cpfs_ignores_non_ascii_digits():
    arabic_indic = "".join(chr(0x0660 + int(d)) for d in "52998224725")
    assert find_unmasked_cpfs(arabic_indic) == []
    assert mask_cpf(arabic_indic) == "*" * 11
