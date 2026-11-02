from pathlib import Path

import pytest

from support.pii import scan_tree

pytestmark = pytest.mark.guard

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"


def test_docs_have_no_unmasked_cpf():
    offenders = scan_tree(DOCS_DIR)

    # Only paths and counts in the message: the CPF itself must never be echoed.
    assert offenders == {}, f"unmasked CPFs found (path: count): {offenders}"
