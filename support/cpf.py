"""CPF check-digit validation (offline, pure)."""

import re

_FORMATTED = re.compile(r"[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}")
_BARE = re.compile(r"[0-9]{11}")


def _check_digit(digits: str) -> int:
    """Modulo-11 check digit for the given leading digits."""
    weight = len(digits) + 1
    total = sum(int(d) * w for d, w in zip(digits, range(weight, 1, -1), strict=True))
    remainder = (total * 10) % 11
    return 0 if remainder == 10 else remainder


def is_valid_cpf(cpf: str | None) -> bool:
    """True for a dotted (``NNN.NNN.NNN-NN``) or bare 11-digit CPF with correct check digits.

    ASCII digits only; ``None`` and any non-string input return False instead of raising.
    """
    if not isinstance(cpf, str):
        return False
    if not (_FORMATTED.fullmatch(cpf) or _BARE.fullmatch(cpf)):
        return False
    digits = re.sub(r"[^0-9]", "", cpf)
    if len(set(digits)) == 1:
        return False
    return digits[9] == str(_check_digit(digits[:9])) and digits[10] == str(
        _check_digit(digits[:10])
    )
