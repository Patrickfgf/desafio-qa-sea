"""PII masking helpers: nothing from a real employee record should be saved or printed raw.

Masked CPF format: ``123.***.***-09`` (first three and last two digits kept).
"""

import copy
import re
from pathlib import Path

CPF_PATTERN = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b")
_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_CPF_DIGITS = 11
_KEPT_TAIL = 2
_DEFAULT_SUFFIXES = (".md", ".txt", ".json", ".html")


def mask_cpf(cpf: str) -> str:
    """Keep the first three and last two digits of a full CPF; mask anything else entirely."""
    digits = re.sub(r"\D", "", cpf)
    if len(digits) != _CPF_DIGITS:
        return "*" * len(cpf)
    return f"{digits[:3]}.***.***-{digits[-_KEPT_TAIL:]}"


def mask_rg(rg: str) -> str:
    """Keep only the last two characters of an RG."""
    if len(rg) <= _KEPT_TAIL:
        return "*" * len(rg)
    return "*" * (len(rg) - _KEPT_TAIL) + rg[-_KEPT_TAIL:]


def mask_name(name: str) -> str:
    """Keep the first letter of each word and mask the rest."""
    return " ".join(word[0] + "*" * (len(word) - 1) for word in name.split())


def mask_birth_date(value: str) -> str:
    """Keep only the year of an ISO date (``YYYY-MM-DD``); mask any other format entirely."""
    if _ISO_DATE.fullmatch(value):
        return f"{value[:4]}-**-**"
    return "*" * len(value)


_FIELD_MASKERS = {
    "name": mask_name,
    "cpf": mask_cpf,
    "rg": mask_rg,
    "birthDay": mask_birth_date,
}


def mask_employee(record: dict) -> dict:
    """Return a deep copy of ``record`` with name, cpf, rg and birthDay masked."""
    masked = copy.deepcopy(record)
    state = masked.get("state")
    employee = state.get("employee") if isinstance(state, dict) else None
    if not isinstance(employee, dict):
        return masked
    for field, masker in _FIELD_MASKERS.items():
        if isinstance(employee.get(field), str):
            employee[field] = masker(employee[field])
    return masked


def mask_text(text: str) -> str:
    """Replace every unmasked CPF found in ``text`` by its masked form."""
    return CPF_PATTERN.sub(lambda match: mask_cpf(match.group()), text)


def find_unmasked_cpfs(text: str) -> list[str]:
    """List every unmasked CPF (formatted or 11 bare digits) found in ``text``."""
    return CPF_PATTERN.findall(text)


def scan_tree(root: Path, suffixes: tuple[str, ...] = _DEFAULT_SUFFIXES) -> dict[str, int]:
    """Map relative path -> count of unmasked CPFs, listing only files with at least one."""
    found: dict[str, int] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        count = len(find_unmasked_cpfs(path.read_text(encoding="utf-8", errors="replace")))
        if count:
            found[path.relative_to(root).as_posix()] = count
    return found
