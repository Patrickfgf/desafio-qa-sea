"""Layout and dead-control defects of the listing page (BUG-026, BUG-027, BUG-028).

Every test is a strict xfail: it states the behaviour we would expect and fails today. Personal
data of third parties is never read: the geometry test returns counts only, and the click test
touches shell elements plus the card of the record the test created itself.
"""

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.support.ui import WebDriverWait

from pages.employee_list_page import EmployeeListPage
from support.api_client import PreconditionError

pytestmark = pytest.mark.ui

WIDE_VIEWPORT = (1920, 1080)
OWN_CARDS_FOR_OVERLAP = 8  # enough cards to fill the list panel (the base itself may be tiny)
EFFECT_WAIT_SECONDS = 2
LAPTOP_VIEWPORT = (1470, 840)  # MacBook screen minus the Chrome tab and address bars
OWN_CARDS_FOR_CLIPPING = 12  # taller than the list panel, whatever the size of the shared base
WHEEL_STEP_PIXELS = 400
MAX_WHEEL_STEPS = 60  # bounded loop: enough to cross any realistic list, never unbounded

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

# The step indicator: each "ITEM" label sits in its own item container.
_STEP_ITEMS_JS = """
return [...document.querySelectorAll('p')]
  .filter(p => /^ITEM\\b/.test(p.textContent.trim()))
  .map(p => p.parentElement);
"""

_NEXT_STEP_JS = """
return [...document.querySelectorAll('button')]
  .find(b => b.textContent.trim() === 'Próximo passo') || null;
"""

# Our own card (found by exact name) and the clickable box of its "..." icon.
_DOTS_HOLDER_JS = """
const name = arguments[0];
const span = [...document.querySelectorAll('span')].find(s => s.textContent.trim() === name);
const img = span && span.parentElement.querySelector('img[src*="dots"]');
return img ? img.parentElement : null;
"""

# Counts elements mounted directly under <body> from now on: menus, modals and drawers are
# rendered there as portals. In-place re-renders of the listing and attribute changes (hover,
# focus) are ignored on purpose: other tests change the listing while this one runs.
_OBSERVE_JS = """
window.__qaPortals = 0;
new MutationObserver(ms => {
  for (const m of ms) {
    window.__qaPortals += [...m.addedNodes].filter(n => n.nodeType === Node.ELEMENT_NODE).length;
  }
}).observe(document.body, {childList: true});
"""

_OVERLAYS_JS = (
    'return document.querySelectorAll(".ant-dropdown, .ant-modal, .ant-drawer, .ant-popover, '
    "[role='menu'], [role='dialog'], [role='listbox']\").length;"
)

# Only calls to the API count as a network reaction; images and stylesheets loaded on hover
# (uncached in CI) do not.
_API_CALLS_JS = (
    "return performance.getEntriesByType('resource')"
    ".filter(e => e.initiatorType === 'fetch' || e.initiatorType === 'xmlhttprequest').length;"
)

# The sidebar is the row that holds the one element whose class list has the token "active".
_SIDEBAR_ITEMS_JS = """
const active = document.querySelector('div[class~="active"]');
return active ? [...active.parentElement.children] : [];
"""


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
    reason='BUG-026: Bloco "A etapa está concluída?" cobre cards da listagem',
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


def _click_has_effect(driver, element) -> bool:
    """Click ``element`` with a real pointer; True if the page reacts before the deadline.

    A reaction is a URL change, a new call to the API, a new element mounted under <body>
    (menus, modals and drawers are portals) or an open menu/dialog. Generic DOM mutations are
    not counted: in CI they come from hover styles and from other tests refreshing the listing,
    which made an inert control look alive (false XPASS). Trade-off: a future fix that reacts
    only in place (inline content, no portal, no URL change, no API call) would keep this test
    XFAIL until the check is widened.
    """
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    url = driver.current_url
    api_calls = driver.execute_script(_API_CALLS_JS)
    overlays = driver.execute_script(_OVERLAYS_JS)
    driver.execute_script(_OBSERVE_JS)

    ActionChains(driver).move_to_element(element).click().perform()

    def reacted(d) -> bool:
        return bool(
            d.current_url != url
            or d.execute_script(_API_CALLS_JS) > api_calls
            or d.execute_script("return window.__qaPortals;")
            or d.execute_script(_OVERLAYS_JS) > overlays
        )

    return _wait_for_effect(driver, reacted)


def _sidebar_icons(driver, _name):
    return driver.execute_script(_SIDEBAR_ITEMS_JS)


def _card_dots(driver, name):
    holder = driver.execute_script(_DOTS_HOLDER_JS, name)
    return [holder] if holder is not None else []


def _next_step_button(driver, _name):
    button = driver.execute_script(_NEXT_STEP_JS)
    return [button] if button is not None else []


def _step_indicator_items(driver, _name):
    return driver.execute_script(_STEP_ITEMS_JS)


CONTROL_GROUPS = {
    "sidebar-icons": (_sidebar_icons, 6),
    "card-dots": (_card_dots, 1),
    "next-step": (_next_step_button, 1),
    "step-indicator": (_step_indicator_items, 9),
}


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-027: Navegação e controles sem efeito",
)
@pytest.mark.parametrize("group", CONTROL_GROUPS)
def test_navigation_control_reacts_to_click(driver, base_url, create_employee, group):
    name = _name_of(create_employee())  # the "..." icon is tested on our own card only
    EmployeeListPage(driver, base_url).open().wait_for_card(name)
    locate, expected = CONTROL_GROUPS[group]
    controls = locate(driver, name)
    if len(controls) != expected:
        raise PreconditionError(f"{group}: found {len(controls)} control(s), expected {expected}")

    dead = 0
    for index in range(len(controls)):
        # Fresh page per control: a reaction of one click must not mask the next one.
        EmployeeListPage(driver, base_url).open().wait_for_card(name)
        dead += 0 if _click_has_effect(driver, locate(driver, name)[index]) else 1

    assert dead == 0, f"{dead} of {len(controls)} {group} control(s) had no effect when clicked"


# The box that clips the listing: nearest ancestor of our card taller inside than on screen.
_LIST_BOX_JS = """
const name = arguments[0];
const span = [...document.querySelectorAll('span')].find(s => s.textContent.trim() === name);
let p = span && span.parentElement;
while (p && p.scrollHeight <= p.clientHeight + 1) p = p.parentElement;
return p || null;
"""

# True when the centre of our card is the topmost thing there and lies inside the list box.
_CARD_REACHABLE_JS = """
const [name, box] = arguments;
const span = [...document.querySelectorAll('span')].find(s => s.textContent.trim() === name);
const card = span && span.parentElement;
if (!card) return false;
const r = card.getBoundingClientRect(), b = box.getBoundingClientRect();
if (r.top < b.top || r.bottom > b.bottom) return false;
const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
return !!hit && card.contains(hit);
"""


def _card_is_reachable(driver, name: str, box) -> bool:
    return bool(driver.execute_script(_CARD_REACHABLE_JS, name, box))


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="BUG-028: Listagem mostra só os primeiros cards e não rola",
)
def test_every_listing_card_is_reachable_by_scrolling(driver, base_url, create_employee):
    # New cards are appended at the end of the list, so our last card is the farthest one.
    names = [_name_of(create_employee()) for _ in range(OWN_CARDS_FOR_CLIPPING)]
    driver.set_window_size(*LAPTOP_VIEWPORT)
    EmployeeListPage(driver, base_url).open().wait_for_card(names[-1])
    box = driver.execute_script(_LIST_BOX_JS, names[-1])
    if box is None:  # nothing overflows: every card already fits on screen
        return

    # A real mouse wheel over the list, as a user would scroll (scrollTop by script would hide it).
    origin = ScrollOrigin.from_element(box)
    for _ in range(MAX_WHEEL_STEPS):
        if _card_is_reachable(driver, names[-1], box):
            break
        ActionChains(driver).scroll_from_origin(origin, 0, WHEEL_STEP_PIXELS).perform()

    assert _card_is_reachable(driver, names[-1], box), (
        f"the last of {OWN_CARDS_FOR_CLIPPING} own cards cannot be brought into view with the "
        f"mouse wheel at {LAPTOP_VIEWPORT[0]}x{LAPTOP_VIEWPORT[1]}"
    )
