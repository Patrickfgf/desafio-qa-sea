"""Employee registration form (inline in the SPA, opened by "+ Adicionar Funcionário")."""

from __future__ import annotations

from pathlib import Path
from typing import Self

from selenium.common.exceptions import TimeoutException
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
_NO_EPI_WRAPPER = (
    By.XPATH,
    "//form//label[contains(@class,'ant-checkbox-wrapper')][.//input[contains(@class,'ant-checkbox-input')]]",
)
_SAVE = (By.CSS_SELECTOR, "form button.save")
_FILE_INPUT = (By.CSS_SELECTOR, "input#file")
_ADD_EPI = (By.CSS_SELECTOR, "form span.addEPI")
_ADD_ACTIVITY = (
    By.XPATH,
    "//form//button[contains(normalize-space(.), 'Adicionar outra atividade')]",
)
_EPI_LABELS = (By.CSS_SELECTOR, "form label[for='epi']")
_SELECTED_ITEM = (By.CSS_SELECTOR, ".ant-select-selection-item")
_VALIDITY_JS = "return [arguments[0].checkValidity(), arguments[0].validationMessage];"


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
            self._clickable(_NO_EPI_WRAPPER).click()

    def choose_activity(self, activity: str) -> None:
        self._choose("activity", activity)

    def choose_epi(self, label: str) -> None:
        self._choose("epi", label)

    def fill_ca_number(self, ca: str) -> None:
        self._type("caNumber", ca)

    def attach_aso(self, path: Path) -> None:
        # File inputs take the path directly; the visible label is only a styled trigger.
        self.wait.until(EC.presence_of_element_located(_FILE_INPUT)).send_keys(str(path))

    def fill_identity(self, employee: dict) -> Self:
        """Name, gender, CPF, birth date and RG (the "active" switch is not touched)."""
        self.fill_name(employee["name"])
        self.choose_gender(employee["gender"])
        self.fill_cpf(employee["cpf"])
        self.fill_birth_date(employee["birthDay"])
        self.fill_rg(employee["rg"])
        return self

    def fill_work(self, employee: dict) -> Self:
        """Role plus the EPI block: the "no EPI" checkbox, or activity, EPI and CA number."""
        self.choose_role(employee["role"])
        # Checkbox means "the worker does NOT use EPI"; both branches of set_no_epi run here.
        self.set_no_epi(not employee["usesEpi"])
        if employee["usesEpi"]:
            self.choose_activity(employee["activity"])
            self.choose_epi(EPI_LABELS[employee["epi"]])
            self.fill_ca_number(employee["caNumber"])
        # Ticking the checkbox removes activity, EPI and CA from the DOM.
        return self

    def fill(self, employee: dict) -> Self:
        """Fill the form the way a user would; every select is chosen explicitly.

        This models what the user means in the UI, not the stored value: the selects display a
        default (e.g. "Cargo 01") but hold nothing until an option is picked, and a new employee
        starts as "Inativo", so state is always set explicitly.
        """
        self.set_active(employee["isActive"])
        return self.fill_identity(employee).fill_work(employee)

    def type_cpf_by_key(self, text: str) -> None:
        """Replace the CPF one keystroke at a time, as a user typing a formatted CPF would."""
        element = self._clickable(_field("cpf"))
        element.clear()
        for char in text:
            element.send_keys(char)

    def selected_text(self, label_for: str) -> str:
        """Option title currently displayed by the select tied to ``label[for=label_for]``."""
        root = self.wait.until(EC.presence_of_element_located(_select_of(label_for)))
        return root.find_element(*_SELECTED_ITEM).get_attribute("title") or ""

    def epi_select_count(self) -> int:
        return len(self.driver.find_elements(*_EPI_LABELS))

    def click_add_epi(self) -> None:
        self._clickable(_ADD_EPI).click()

    def click_add_activity(self) -> None:
        self._clickable(_ADD_ACTIVITY).click()

    def wait_for_epi_select_count_above(self, count: int, timeout: float = 3) -> bool:
        """True when more than ``count`` EPI selects show up before the deadline."""
        try:
            WebDriverWait(self.driver, timeout).until(lambda _: self.epi_select_count() > count)
        except TimeoutException:
            return False
        return True

    def field_validity(self, name: str) -> tuple[bool, str]:
        """(``checkValidity()``, ``validationMessage``) of the named input; no value is read."""
        element = self.wait.until(EC.presence_of_element_located(_field(name)))
        valid, message = self.driver.execute_script(_VALIDITY_JS, element)
        return bool(valid), str(message)

    def is_open(self) -> bool:
        return bool(self.driver.find_elements(*_FORM))

    def wait_until_closed(self, timeout: float = 3) -> bool:
        """True when the form disappears before the deadline (an explicit wait, never a sleep)."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(_FORM))
        except TimeoutException:
            return False
        return True

    def submit(self) -> None:
        """Click "Salvar" without waiting; the browser may block it with native validation."""
        # "Adicionar outra atividade" is an implicit submit and is deliberately never used here.
        self._clickable(_SAVE).click()

    def save(self) -> EmployeeListPage:
        self.submit()
        self.wait.until(EC.invisibility_of_element_located(_FORM))
        # No reload here: the app fires its listing GET in parallel with the POST (BUG-013), so
        # the listing it shows can be stale. Callers re-open the page to read persisted data.
        return EmployeeListPage(self.driver, self.base_url)
