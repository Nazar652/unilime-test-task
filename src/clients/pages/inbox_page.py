import logging
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from src.clients.pages.base_page import BasePage
from src.domain.models import EmailMessage, InboxItem, TempEmail

logger = logging.getLogger(__name__)

TOOLTIP_FORMAT = '%m/%d/%Y, %I:%M:%S %p'


class InboxPage(BasePage):
    ADDRESS_INPUT = (By.CSS_SELECTOR, 'input#email')
    NEW_ADDRESS_BUTTON = (By.CSS_SELECTOR, 'button[data-qa="random-button"]')
    MESSAGE_ROW = (By.CSS_SELECTOR, 'li[data-qa="message"]')
    ROW_SENDER = (By.CSS_SELECTOR, '[data-qa="heading"] .truncate')
    ROW_SUBJECT = (By.CSS_SELECTOR, '[data-qa="message-subject"]')
    ROW_DATE = (By.CSS_SELECTOR, '[data-qa="date"]')
    DETAIL_SENDER = (By.CSS_SELECTOR, 'article[data-qa="message-page"] [data-qa="from"]')
    DETAIL_SUBJECT = (By.CSS_SELECTOR, 'article[data-qa="message-page"] [data-qa="message-subject"]')
    DETAIL_DATE = (By.CSS_SELECTOR, 'article[data-qa="message-page"] [data-qa="date"]')
    DETAIL_BODY = (By.CSS_SELECTOR, 'article[data-qa="message-page"] .overflow-auto')
    SHOWN_TOOLTIP = (By.CSS_SELECTOR, '.v-popper__popper--shown .v-popper__inner')
    MESSAGES_TIMEOUT = 6

    def open(self) -> None:
        logger.debug('opening %s', self.config.base_url)
        self.driver.get(self.config.base_url)
        self.wait.until(expected_conditions.presence_of_element_located(self.ADDRESS_INPUT))

    def read_current_email(self) -> TempEmail:
        address = self.wait.until(self.read_address)
        return TempEmail(address=address)

    def read_inbox(self) -> list[InboxItem]:
        self.wait.until(self.read_address)
        self.wait_for_messages()
        count = len(self.driver.find_elements(*self.MESSAGE_ROW))
        logger.debug('inbox has %d messages', count)
        items: list[InboxItem] = []
        for index in range(count):
            rows = self.driver.find_elements(*self.MESSAGE_ROW)
            if index >= len(rows):
                break
            items.append(self.harvest_row(rows[index]))
        return items

    def harvest_row(self, row: WebElement) -> InboxItem:
        sender = self.element_label(row, self.ROW_SENDER)
        subject = self.element_label(row, self.ROW_SUBJECT)
        received_at = self.read_absolute_date(row.find_element(*self.ROW_DATE))
        message_id = self.open_row(row)
        return InboxItem(id=message_id, sender=sender, subject=subject, received_at=received_at)

    def open_row(self, row: WebElement) -> str:
        origin = self.driver.current_url
        row.click()
        self.wait.until(lambda driver: '/message/' in driver.current_url)
        message_id = self.driver.current_url.rsplit('/', 1)[-1]
        logger.debug('harvested message id %s', message_id)
        self.driver.back()
        self.wait.until(lambda driver: driver.current_url == origin)
        self.wait.until(expected_conditions.presence_of_element_located(self.MESSAGE_ROW))
        return message_id

    def read_message(self, message_id: str) -> EmailMessage | None:
        logger.debug('reading message %s', message_id)
        self.driver.get(self.message_url(message_id))
        if not self.message_loaded(message_id):
            logger.debug('message %s not found', message_id)
            return None
        return EmailMessage(
            id=message_id,
            sender=self.detail_text(self.DETAIL_SENDER),
            subject=self.detail_text(self.DETAIL_SUBJECT),
            received_at=self.read_absolute_date(self.driver.find_element(*self.DETAIL_DATE)),
            body=self.detail_text(self.DETAIL_BODY),
        )

    def message_loaded(self, message_id: str) -> bool:
        marker = f'/message/{message_id}'

        def settled(driver: WebDriver) -> bool:
            ready = bool(driver.find_elements(*self.DETAIL_SENDER))
            return ready or marker not in driver.current_url

        try:
            self.wait.until(settled)
        except TimeoutException:
            return False
        return bool(self.driver.find_elements(*self.DETAIL_SENDER))

    def request_new_email(self) -> TempEmail:
        previous = self.read_address(self.driver)
        self.driver.find_element(*self.NEW_ADDRESS_BUTTON).click()
        address = self.wait.until(lambda driver: self.changed_address(driver, previous))
        logger.info('generated new address')
        return TempEmail(address=address)

    def changed_address(self, driver: WebDriver, previous: str) -> str:
        current = self.read_address(driver)
        return current if current and current != previous else ''

    def read_address(self, driver: WebDriver) -> str:
        element = driver.find_element(*self.ADDRESS_INPUT)
        return (element.get_attribute('value') or '').strip()

    def message_url(self, message_id: str) -> str:
        return f'{self.config.base_url}/message/{message_id}'

    def wait_for_messages(self) -> None:
        try:
            WebDriverWait(self.driver, self.MESSAGES_TIMEOUT).until(
                expected_conditions.presence_of_element_located(self.MESSAGE_ROW)
            )
        except TimeoutException:
            pass

    def read_absolute_date(self, date_element: WebElement) -> str:
        ActionChains(self.driver).move_to_element(date_element).perform()
        tooltip = self.wait.until(
            expected_conditions.visibility_of_element_located(self.SHOWN_TOOLTIP)
        )
        return self.parse_date((tooltip.text or '').strip())

    def parse_date(self, raw: str) -> str:
        try:
            return datetime.strptime(raw, TOOLTIP_FORMAT).isoformat()
        except ValueError:
            return raw

    def element_label(self, scope: WebElement, locator: tuple[str, str]) -> str:
        element = scope.find_element(*locator)
        return (element.get_attribute('title') or element.text or '').strip()

    def detail_text(self, locator: tuple[str, str]) -> str:
        return self.driver.find_element(*locator).text.strip()
