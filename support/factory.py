"""Synthetic employee factory: only fake data, always tagged with ``TEST_PREFIX``."""

from uuid import uuid4

from faker import Faker

TEST_PREFIX = "QA-AUTO-"
GENDERS = ("masculino", "feminino")
ROLES = ("Cargo 01", "Cargo 02", "Cargo 03", "Cargo 04", "Cargo 05")
ACTIVITIES = ("Ativid 01", "Ativid 02", "Ativid 03", "Ativid 04", "Ativid 05")
# value -> label, copied verbatim from the app bundle (including the "oculor" typo in the value).
EPI_LABELS = {
    "capacete-de-segurança": "Capacete de segurança",
    "luvas-descartaveis": "Luvas descartáveis",
    "oculor-de-proteçao": "Óculos de proteção",
    "calçado-de-segurança": "Calçado de Segurança",
    "protetor-auditivo": "Protetor auditivo",
}
EMPLOYEE_FIELDS = (
    "isActive",
    "name",
    "gender",
    "cpf",
    "birthDay",
    "rg",
    "role",
    "usesEpi",
    "activity",
    "epi",
    "caNumber",
)
_MIN_AGE = 18
_MAX_AGE = 65
_RG_PATTERN = "#" * 7
_CA_PATTERN = "#" * 5

fake = Faker("pt_BR")


def build_employee(**overrides) -> dict:
    """Return a fresh synthetic employee dict; unknown override keys raise ``KeyError``."""
    unknown = sorted(set(overrides) - set(EMPLOYEE_FIELDS))
    if unknown:
        raise KeyError(f"Unknown employee field(s): {', '.join(unknown)}")
    employee = {
        "isActive": True,
        "name": f"{TEST_PREFIX}{fake.name()} {uuid4().hex[:6]}",
        "gender": fake.random_element(GENDERS),
        "cpf": "".join(ch for ch in fake.cpf() if ch.isdigit()),
        "birthDay": fake.date_of_birth(minimum_age=_MIN_AGE, maximum_age=_MAX_AGE).isoformat(),
        "rg": fake.numerify(_RG_PATTERN),
        "role": fake.random_element(ROLES),
        "usesEpi": True,
        "activity": fake.random_element(ACTIVITIES),
        "epi": fake.random_element(tuple(EPI_LABELS)),
        "caNumber": fake.numerify(_CA_PATTERN),
    }
    return {**employee, **overrides}


def as_payload(employee: dict) -> dict:
    """Wrap an employee in the API record shape (without ``id``)."""
    return {"state": {"employee": employee}}
