"""Employee listing: the SPA's single page at ``/``."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

if TYPE_CHECKING:
    from pages.employee_form_page import EmployeeFormPage

_ADD = (By.XPATH, "//button[contains(normalize-space(.), 'Adicionar Funcionário')]")
_ACTIVE_ONLY = (By.XPATH, "//button[contains(normalize-space(.), 'Ver apenas ativos')]")
_CLEAR = (By.CSS_SELECTOR, "button.clear")
_COUNTER = re.compile(r"Ativos\s+(\d+)\s*/\s*(\d+)")


@dataclass(frozen=True)
class EmployeeCard:
    name: str
    cpf: str
    activity: str
    role: str


def _xpath_literal(text: str) -> str:
    if "'" not in text:
        return f"'{text}'"
    parts = text.split("'")
    return "concat(" + ', "\'", '.join(f"'{p}'" for p in parts) + ")"


def _name_span(name: str) -> tuple[str, str]:
    # Exact text match on the name span; hashed styled-components classes are not used.
    return (By.XPATH, f"//span[normalize-space(text())={_xpath_literal(name)}]")


class EmployeeListPage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    def open(self) -> Self:
        self.driver.get(self.base_url)
        self.wait.until(EC.visibility_of_element_located(_ADD))
        return self

    def click_add(self) -> EmployeeFormPage:
        # Imported here: the form page imports this module for its save() return type.
        from pages.employee_form_page import EmployeeFormPage

        self.wait.until(EC.element_to_be_clickable(_ADD)).click()
        return EmployeeFormPage(self.driver, self.base_url)

    def toggle_active_only(self) -> None:
        self.wait.until(EC.element_to_be_clickable(_ACTIVE_ONLY)).click()

    def clear_filters(self) -> None:
        self.wait.until(EC.element_to_be_clickable(_CLEAR)).click()

    def counter(self) -> tuple[int, int]:
        """Read "Ativos X/Y" from the page text: (active, total)."""
        body = self.driver.find_element(By.TAG_NAME, "body")
        match = self.wait.until(lambda _: _COUNTER.search(body.text))
        return int(match.group(1)), int(match.group(2))

    def find_card(self, name: str) -> EmployeeCard | None:
        spans = self.driver.find_elements(*_name_span(name))
        if not spans:
            return None
        # Sibling container of the name span: formatted CPF, [activity], role. Cards without an
        # activity render only two divs, so role is always the last one.
        cells = [
            (cell.get_attribute("textContent") or "").strip()
            for cell in spans[0].find_elements(By.XPATH, "./following-sibling::*[1]/div")
        ]
        activity = cells[1] if len(cells) == 3 else ""
        return EmployeeCard(name=name, cpf=cells[0], activity=activity, role=cells[-1])

    def wait_for_card(self, name: str, timeout: float = 10) -> EmployeeCard:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(_name_span(name))
            )
        except TimeoutException as exc:
            raise AssertionError("Employee card did not appear in the listing") from exc
        card = self.find_card(name)
        assert card is not None
        return card
