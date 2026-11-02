import pytest

from support.cpf import is_valid_cpf

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("cpf", ["52998224725", "529.982.247-25"])
def test_accepts_valid_cpf_with_or_without_mask(cpf):
    assert is_valid_cpf(cpf)


@pytest.mark.parametrize(
    "cpf",
    ["52998224726", "11111111111", "123", "5299822472a", "", "529.982.24725", "529982247251"],
)
def test_rejects_invalid_cpf(cpf):
    assert not is_valid_cpf(cpf)
