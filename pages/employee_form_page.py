"""Employee registration form (inline in the SPA, opened by "+ Adicionar Funcionário")."""

from __future__ import annotations

from pathlib import Path
from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.components.antd import select_option, set_react_input, set_switch
from pages.employee_list_page import EmployeeListPage
from support.factory import EPI_LABELS

_GENDER_LABELS = {"masculino": "Masculino", "feminino": "Feminino"}
_FORM = (By.CSS_SELECTOR, "form")
_ACTIVE_SWITCH = (By.CSS_SELECTOR, "form button[role='switch']")
_NO_EPI_CHECKBOX = (By.CSS_SELECTOR, "form .ant-checkbox-input")
_SAVE = (By.CSS_SELECTOR, "form button.save")
_FILE_INPUT = (By.CSS_SELECTOR, "input#file")


def _field(name: str) -> tuple[str, str]:
    return (By.CSS_SELECTOR, f"form input[name='{name}']")


def _select_of(label_for: str) -> tuple[str, str]:
    # Labels carry for="role"/"activity"/"epi"; the Ant Select is the label's sibling.
    return (
        By.XPATH,
        f"//form//label[@for='{label_for}']/following-sibling::div[contains(@class,'ant-select')]",
    )


class EmployeeFormPage:
    def __init__(self, driver: WebDriver, base_url: str, timeout: float = 10):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)
        self.wait.until(EC.visibility_of_element_located(_FORM))

    def _clickable(self, locator: tuple[str, str]) -> WebElement:
        element = self.wait.until(EC.presence_of_element_located(locator))
        # Fields below the fold must be scrolled to before they can receive a click.
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        return self.wait.until(EC.element_to_be_clickable(locator))

    def _type(self, name: str, text: str) -> None:
        element = self._clickable(_field(name))
        element.clear()
        element.send_keys(text)

    def _choose(self, label_for: str, label: str) -> None:
        root = self.wait.until(EC.presence_of_element_located(_select_of(label_for)))
        select_option(self.driver, root, label)

    def set_active(self, active: bool) -> None:
        set_switch(self._clickable(_ACTIVE_SWITCH), active)

    def fill_name(self, name: str) -> None:
        self._type("name", name)

    def choose_gender(self, gender: str) -> None:
        label = _GENDER_LABELS[gender]
        locator = (
            By.XPATH,
            f"//form//label[contains(@class,'ant-radio-wrapper')][.//span[text()='{label}']]",
        )
        self._clickable(locator).click()

    def fill_cpf(self, cpf: str) -> None:
        self._type("cpf", cpf)

    def fill_birth_date(self, iso_date: str) -> None:
        element = self.wait.until(EC.presence_of_element_located(_field("birthDay")))
        set_react_input(self.driver, element, iso_date)

    def fill_rg(self, rg: str) -> None:
        self._type("rg", rg)

    def choose_role(self, role: str) -> None:
        self._choose("role", role)

    def set_no_epi(self, checked: bool) -> None:
        box = self.wait.until(EC.presence_of_element_located(_NO_EPI_CHECKBOX))
        if box.is_selected() != checked:
            # The native input is visually hidden by antd; its wrapper label takes the click.
            self._clickable(_NO_EPI_CHECKBOX).click()

    def choose_activity(self, activity: str) -> None:
        self._choose("activity", activity)

    def choose_epi(self, label: str) -> None:
        self._choose("epi", label)

    def fill_ca_number(self, ca: str) -> None:
        self._type("caNumber", ca)

    def attach_aso(self, path: Path) -> None:
        # File inputs take the path directly; the visible label is only a styled trigger.
        self.wait.until(EC.presence_of_element_located(_FILE_INPUT)).send_keys(str(path))

    def fill(self, employee: dict) -> Self:
        """Fill the form the way a user would; every select is chosen explicitly.

        This models what the user means in the UI, not the stored value: the selects display a
        default (e.g. "Cargo 01") but hold nothing until an option is picked, and a new employee
        starts as "Inativo", so state is always set explicitly.
        """
        self.set_active(employee["isActive"])
        self.fill_name(employee["name"])
        self.choose_gender(employee["gender"])
        self.fill_cpf(employee["cpf"])
        self.fill_birth_date(employee["birthDay"])
        self.fill_rg(employee["rg"])
        self.choose_role(employee["role"])
        if employee["usesEpi"]:
            # Checkbox stays unticked: it means "the worker does NOT use EPI".
            self.choose_activity(employee["activity"])
            self.choose_epi(EPI_LABELS[employee["epi"]])
            self.fill_ca_number(employee["caNumber"])
        else:
            # Ticking removes activity, EPI and CA from the DOM.
            self.set_no_epi(True)
        return self

    def save(self) -> EmployeeListPage:
        # "Adicionar outra atividade" is an implicit submit and is deliberately never clicked.
        self._clickable(_SAVE).click()
        self.wait.until(EC.invisibility_of_element_located(_FORM))
        # No reload here: the app does not refresh the listing after saving.
        return EmployeeListPage(self.driver, self.base_url)
