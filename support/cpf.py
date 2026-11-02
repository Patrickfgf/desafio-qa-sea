"""CPF check-digit validation (offline, pure)."""

import re

_CPF_DIGITS = 11
_FORMATTED = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
_BARE = re.compile(r"\d{11}")


def _check_digit(digits: str) -> int:
    """Modulo-11 check digit for the given leading digits."""
    weight = len(digits) + 1
    total = sum(int(d) * w for d, w in zip(digits, range(weight, 1, -1), strict=True))
    remainder = (total * 10) % 11
    return 0 if remainder == 10 else remainder


def is_valid_cpf(cpf: str) -> bool:
    """True for a masked (``529.982.247-25``) or bare-digit CPF with correct check digits."""
    if not (_FORMATTED.fullmatch(cpf) or _BARE.fullmatch(cpf)):
        return False
    digits = re.sub(r"\D", "", cpf)
    if len(set(digits)) == 1:
        return False
    return digits[9] == str(_check_digit(digits[:9])) and digits[10] == str(
        _check_digit(digits[:10])
    )
