"""Page-level defects first identified in a public 2025 repository and reproduced here (EXT-NN).

Origin and attribution live in ``docs/relatorio-de-defeitos.md``. Every test is a strict xfail:
it states the behaviour we would expect and fails today. Personal data of third parties is never
read: the geometry test returns counts only, and the other tests read shell texts (labels,
title) or the card of the record the test created itself.
"""

import unicodedata

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.employee_list_page import EmployeeListPage
from support.api_client import PreconditionError

pytestmark = pytest.mark.ui

WIDE_VIEWPORT = (1920, 1080)
OWN_CARDS_FOR_OVERLAP = 8  # enough cards to fill the list panel (the base itself may be tiny)
EFFECT_WAIT_SECONDS = 2
TEMPLATE_TITLE = "Vite + React + TS"
CONCLUDED_LABEL = "CONCLUÍDO"

_BLOCK_JS = """
const span = [...document.querySelectorAll('span')]
  .find(s => s.textContent.trim() === 'A etapa está concluída?');
return span ? span.parentElement : null;
"""

# Counts cards (structural match: a name span followed by 2-3 rows, outside the form) and how many
# overlap the absolute-positioned block. Returns numbers only, never text.
_OVERLAP_COUNT_JS = """
const block = arguments[0];
const b = block.getBoundingClientRect();
let cards = 0, overlapping = 0;
for (const s of document.querySelectorAll('span')) {
  if (s.closest('form') || block.contains(s)) continue;
  const next = s.nextElementSibling;
  if (!next || next.querySelector('span')) continue;
  const rows = next.querySelectorAll(':scope > div').length;
  if (rows < 2 || rows > 3) continue;
  const r = s.parentElement.getBoundingClientRect();
  cards += 1;
  const w = Math.min(r.right, b.right) - Math.max(r.left, b.left);
  const h = Math.min(r.bottom, b.bottom) - Math.max(r.top, b.top);
  if (w > 0 && h > 0) overlapping += 1;
}
return [cards, overlapping];
"""

# Scrolls the list that holds our own card (found by exact name) to its start or end.
_SCROLL_LIST_JS = """
const name = arguments[0];
const span = [...document.querySelectorAll('span')].find(s => s.textContent.trim() === name);
let p = span && span.parentElement;
while (p && p.scrollHeight <= p.clientHeight + 1) p = p.parentElement;
if (!p) return false;
p.scrollTop = arguments[1] === 'end' ? p.scrollHeight : 0;
return true;
"""

_STEP_LABELS_JS = """
return [...document.querySelectorAll('p')]
  .map(p => p.textContent.trim()).filter(t => /^ITEM\\b/.test(t));
"""

_CONCLUDED_LABEL_JS = """
const p = [...document.querySelectorAll('p')].find(x => /^CONCLU/i.test(x.textContent.trim()));
return p ? p.textContent.trim() : null;
"""

# The sidebar is the row that holds the one element whose class list has the token "active".
_SIDEBAR_ITEMS_JS = """
const active = document.querySelector('div[class~="active"]');
return active ? [...active.parentElement.children] : [];
"""

_ACTIVE_FLAGS_JS = """
return arguments[0].map(e => e.classList.contains('active'));
"""

_OWN_DOTS_HOLDER_JS = """
const name = arguments[0];
const span = [...document.querySelectorAll('span')].find(s => s.textContent.trim() === name);
const img = span && span.parentElement.querySelector('img[src*="dots"]');
return img ? img.parentElement : null;
"""

_OPEN_MENUS_JS = (
    "return document.querySelectorAll("
    "\".ant-dropdown, .ant-modal, [role='menu'], [role='dialog']\").length;"
)


def _name_of(created: dict) -> str:
    return created["state"]["employee"]["name"]


def _wait_for_effect(driver, condition) -> bool:
    """True when ``condition(driver)`` holds before the deadline (explicit wait, no sleep)."""
    try:
        WebDriverWait(driver, EFFECT_WAIT_SECONDS).until(condition)
    except TimeoutException:
        return False
    return True


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason='EXT-02: Bloco "A etapa está concluída?" sobrepõe a listagem',
)
def test_step_block_does_not_overlap_the_listing(driver, base_url, create_employee):
    names = [_name_of(create_employee()) for _ in range(OWN_CARDS_FOR_OVERLAP)]
    driver.set_window_size(*WIDE_VIEWPORT)
    EmployeeListPage(driver, base_url).open().wait_for_card(names[-1])
    block = driver.execute_script(_BLOCK_JS)
    if block is None:
        raise PreconditionError("the 'A etapa está concluída?' block was not found")

    overlapping = 0
    for position in ("top", "end"):
        driver.execute_script(_SCROLL_LIST_JS, names[0], position)
        cards, hits = driver.execute_script(_OVERLAP_COUNT_JS, block)
        if cards < OWN_CARDS_FOR_OVERLAP:
            raise PreconditionError(f"only {cards} card(s) rendered in the listing")
        overlapping = max(overlapping, hits)

    assert overlapping == 0, f"the step block overlaps {overlapping} listing card(s) at 1920x1080"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason='EXT-03: Rótulos "ITEM 1" repetidos na trilha de etapas',
)
def test_step_labels_are_distinct(driver, base_url):
    EmployeeListPage(driver, base_url).open()

    labels = driver.execute_script(_STEP_LABELS_JS)

    # No "ITEM" label left means the placeholder was replaced (the xfail then turns XPASS).
    distinct = len(set(labels))
    assert distinct == len(labels), (
        f"{len(labels)} step labels start with 'ITEM' but only {distinct} distinct value(s)"
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="EXT-04: Rótulo CONCLUIDO sem acento",
)
def test_concluded_label_is_accented_in_both_states(driver, base_url):
    EmployeeListPage(driver, base_url).open()
    block = driver.execute_script(_BLOCK_JS)
    switch = block.find_element(By.CSS_SELECTOR, "button[role='switch']") if block else None
    first = driver.execute_script(_CONCLUDED_LABEL_JS)
    if switch is None or first is None:
        raise PreconditionError("the 'concluído' label or its switch was not found")
    switch.click()
    _wait_for_effect(driver, lambda d: switch.get_attribute("aria-checked") == "true")
    second = driver.execute_script(_CONCLUDED_LABEL_JS)

    normalized = {unicodedata.normalize("NFC", t or "") for t in (first, second)}
    assert normalized == {CONCLUDED_LABEL}, f"label texts in the two states: {sorted(normalized)}"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="EXT-05: Itens da barra lateral não reagem ao clique",
)
def test_sidebar_item_becomes_active_when_clicked(driver, base_url):
    EmployeeListPage(driver, base_url).open()
    items = driver.execute_script(_SIDEBAR_ITEMS_JS)
    if len(items) < 2:
        raise PreconditionError(f"sidebar not found ({len(items)} item(s))")

    unresponsive = 0
    for index, item in enumerate(items):
        ActionChains(driver).move_to_element(item).click().perform()
        became_active = _wait_for_effect(
            driver, lambda d, i=index: d.execute_script(_ACTIVE_FLAGS_JS, items)[i]
        )
        unresponsive += 0 if became_active else 1

    assert unresponsive == 0, f"{unresponsive} of {len(items)} sidebar icons did not become active"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="EXT-06: Rótulos abreviados e capitalização inconsistente nos selects",
)
def test_select_option_labels_are_spelled_out_and_consistent(driver, base_url):
    form = EmployeeListPage(driver, base_url).open().click_add()  # nothing is saved here

    activities = form.option_titles("activity")
    epis = form.option_titles("epi")

    problems = []
    abbreviated = [a for a in activities if a.startswith("Ativid ")]
    if abbreviated:
        problems.append(f"{len(abbreviated)} of {len(activities)} activity labels use 'Ativid'")
    # Style of the other options: only the first word is capitalized.
    odd_case = [e for e in epis if any(word[:1].isupper() for word in e.split(" ")[1:])]
    if odd_case:
        problems.append(f"EPI label(s) capitalized unlike the others: {odd_case}")
    assert not problems, "; ".join(problems)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="EXT-07: Botão de três pontos do card não abre menu",
)
def test_card_dots_button_opens_a_menu(driver, base_url, create_employee):
    name = _name_of(create_employee())
    EmployeeListPage(driver, base_url).open().wait_for_card(name)
    holder = driver.execute_script(_OWN_DOTS_HOLDER_JS, name)
    if holder is None:
        raise PreconditionError("the dots button of our own card was not found")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", holder)
    nodes_before = driver.execute_script("return document.querySelectorAll('*').length;")

    ActionChains(driver).move_to_element(holder).click().perform()
    opened = _wait_for_effect(driver, lambda d: d.execute_script(_OPEN_MENUS_JS) > 0)

    nodes_after = driver.execute_script("return document.querySelectorAll('*').length;")
    assert opened, f"no menu or dialog opened (DOM nodes {nodes_before} -> {nodes_after})"


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="EXT-08: Título da aba é o do template Vite",
)
def test_page_title_is_not_the_template_default(driver, base_url):
    EmployeeListPage(driver, base_url).open()

    title = driver.title

    assert title.strip().lower() != TEMPLATE_TITLE.lower(), f"tab title is {title!r}"
