"""Redaction of third-party personal data from the page before a failure screenshot.

The listing shows every employee in the shared base. A screenshot must only keep our own
synthetic cards (name prefix ``QA-AUTO-``) and must never show a full CPF.
"""

from selenium.webdriver.remote.webdriver import WebDriver

from support.factory import TEST_PREFIX

# Fail closed. A card is a name <span> followed by a sibling container holding at least two
# divs (CPF, [activity], role: cards without an activity have only two). Every card whose name
# does not start with our prefix is hidden. A MutationObserver re-applies the rules to anything
# React renders after the call, so the screenshot never races a re-render.
_REDACT_JS = r"""
const prefix = arguments[0];
const cpf = /(?<!\d)(\d{3})\.?\d{3}\.?\d{3}-?(\d{2})(?!\d)/g;
function apply() {
  for (const span of document.querySelectorAll('span')) {
    const next = span.nextElementSibling;
    if (!next || next.querySelectorAll(':scope > div').length < 2) continue;
    const card = span.parentElement;
    if (!span.textContent.trim().startsWith(prefix)) card.style.visibility = 'hidden';
  }
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const masked = node.nodeValue.replace(cpf, '$1.***.***-$2');
    if (masked !== node.nodeValue) node.nodeValue = masked;
  }
}
apply();
if (window.__qaRedactionObserver) window.__qaRedactionObserver.disconnect();
const observer = new MutationObserver(() => {
  observer.disconnect();
  apply();
  observer.observe(document.body, {childList: true, subtree: true, characterData: true});
});
observer.observe(document.body, {childList: true, subtree: true, characterData: true});
window.__qaRedactionObserver = observer;
"""


def redact_page(driver: WebDriver) -> None:
    """Hide foreign employee cards and mask CPF-like text in the current page (in place).

    Stays active as an observer so cards rendered after this call are redacted too.
    """
    driver.execute_script(_REDACT_JS, TEST_PREFIX)
