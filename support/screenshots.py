"""Redaction of third-party personal data from the page before a failure screenshot.

The listing shows every employee in the shared base. A screenshot must only keep our own
synthetic cards (name prefix ``QA-AUTO-``) and must never show a full CPF.
"""

from selenium.webdriver.remote.webdriver import WebDriver

from support.factory import TEST_PREFIX

# A card is the parent of the name <span>; its next sibling holds the CPF/activity/role divs.
_REDACT_JS = """
const prefix = arguments[0];
for (const span of document.querySelectorAll('span')) {
  const next = span.nextElementSibling;
  if (!next || next.querySelectorAll(':scope > div').length !== 3) continue;
  if (!span.textContent.trim().startsWith(prefix)) {
    span.parentElement.style.visibility = 'hidden';
  }
}
const cpf = /(?<!\\d)(\\d{3})\\.?\\d{3}\\.?\\d{3}-?(\\d{2})(?!\\d)/g;
const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
const nodes = [];
while (walker.nextNode()) nodes.push(walker.currentNode);
for (const node of nodes) {
  node.nodeValue = node.nodeValue.replace(cpf, '$1.***.***-$2');
}
"""


def redact_page(driver: WebDriver) -> None:
    """Hide foreign employee cards and mask CPF-like text in the current page (in place)."""
    driver.execute_script(_REDACT_JS, TEST_PREFIX)
