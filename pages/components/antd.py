"""Helpers for Ant Design widgets (Select, Switch) and React-controlled inputs."""

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

_SET_VALUE_JS = """
const el = arguments[0];
const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
setter.call(el, arguments[1]);
el.dispatchEvent(new Event('input', {bubbles: true}));
el.dispatchEvent(new Event('change', {bubbles: true}));
"""


def _literal(text: str) -> str:
    """Double-quoted literal usable in both CSS and XPath (labels here never contain quotes)."""
    if '"' in text:
        raise ValueError("label must not contain a double quote")
    return f'"{text}"'


def _selected(select_root: WebElement, label: str) -> list[WebElement]:
    return select_root.find_elements(
        By.CSS_SELECTOR, f".ant-select-selection-item[title={_literal(label)}]"
    )


def _pick(driver: WebDriver, select_root: WebElement, title_test: str, timeout: float) -> None:
    """Open the select and click the first option whose title satisfies ``title_test`` (XPath).

    Antd keeps every dropdown it ever opened in <body>, and a closing one stays rendered during
    its fade-out. Matching ``.ant-select-dropdown:not(.ant-select-dropdown-hidden)`` alone can
    therefore hit the PREVIOUS select's options; those are not clickable and the click lands on
    the form instead (ElementClickInterceptedException). So the dropdown is found through the
    combobox's ``aria-controls`` listbox id, which belongs to this select only.
    """
    wait = WebDriverWait(driver, timeout)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_root)
    listbox_id = select_root.find_element(By.CSS_SELECTOR, "input[role='combobox']").get_attribute(
        "aria-controls"
    )
    wait.until(EC.element_to_be_clickable(select_root)).click()
    option = (
        By.XPATH,
        f"//div[@id={_literal(listbox_id)}]"
        "/ancestor::div[contains(@class,'ant-select-dropdown')]"
        "[not(contains(@class,'ant-select-dropdown-hidden'))]"
        f"//div[contains(@class,'ant-select-item-option')][{title_test}]",
    )
    wait.until(EC.element_to_be_clickable(option)).click()


def select_option(
    driver: WebDriver, select_root: WebElement, label: str, timeout: float = 10
) -> None:
    """Open an Ant Select, click the option titled ``label`` and wait until it is displayed."""
    wait = WebDriverWait(driver, timeout)
    if _selected(select_root, label):
        # The app displays a default (e.g. "Cargo 01") but stores nothing for it, and antd fires
        # no change when the displayed option is clicked again. Pick another option first, so
        # choosing ``label`` is a real change, as it is for a user who switches away and back.
        _pick(driver, select_root, f"@title!={_literal(label)}", timeout)
        wait.until(lambda _: not _selected(select_root, label))
        # Let the first dropdown finish closing before the root is clicked again.
        wait.until(
            lambda _: (
                select_root.find_element(By.CSS_SELECTOR, "input[role='combobox']").get_attribute(
                    "aria-expanded"
                )
                == "false"
            )
        )
    _pick(driver, select_root, f"@title={_literal(label)}", timeout)
    wait.until(lambda _: _selected(select_root, label))


def set_switch(switch: WebElement, on: bool) -> None:
    """Click an Ant Switch only when its ``aria-checked`` differs from the wanted state."""
    if (switch.get_attribute("aria-checked") == "true") != on:
        switch.click()


def set_react_input(driver: WebDriver, element: WebElement, value: str) -> None:
    """Set an input through the native value setter plus bubbling ``input``/``change`` events.

    Used for ``type=date``: typing into it depends on the browser locale (dd/mm/yyyy vs
    mm/dd/yyyy), while the native setter always takes ISO ``YYYY-MM-DD``. React tracks the value
    itself, so the native setter (not ``el.value = ...``) is needed for onChange to fire.
    """
    driver.execute_script(_SET_VALUE_JS, element, value)
