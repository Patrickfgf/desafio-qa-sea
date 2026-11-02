"""The screenshot redaction, checked against a tiny local page (no live app involved)."""

import pytest
from selenium.webdriver.common.by import By

from support.screenshots import redact_page

_CARD = (
    "<div id='{id}'><span>{name}</span><div><div>{cpf}</div><div>A</div><div>R</div></div></div>"
)
_PAGE = (
    "<html><body>"
    + _CARD.format(id="own", name="QA-AUTO-Someone", cpf="123.456.789-09")
    + _CARD.format(id="foreign", name="Third Party", cpf="98765432100")
    + "<p id='free'>cpf 111.222.333-44 end</p></body></html>"
)


@pytest.mark.ui
def test_redaction_hides_foreign_cards_and_masks_cpf(driver, tmp_path):
    page = tmp_path / "page.html"
    page.write_text(_PAGE, encoding="utf-8")
    driver.get(page.as_uri())

    redact_page(driver)

    foreign = driver.find_element(By.CSS_SELECTOR, "#foreign")
    own = driver.find_element(By.CSS_SELECTOR, "#own")
    assert foreign.value_of_css_property("visibility") == "hidden"
    assert own.value_of_css_property("visibility") == "visible"
    text = driver.find_element(By.TAG_NAME, "body").get_attribute("textContent")
    assert "456.789" not in text
    assert "98765432100" not in text
    assert "222.333" not in text
    assert "123.***.***-09" in text
    assert "111.***.***-44" in text
