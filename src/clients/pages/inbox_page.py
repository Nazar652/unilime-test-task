from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions

from src.clients.pages.base_page import BasePage
from src.domain.models import EmailMessage, InboxItem, TempEmail


class InboxPage(BasePage):
    ADDRESS_INPUT = (By.CSS_SELECTOR, 'input#email')

    def open(self) -> None:
        self.driver.get(self.config.base_url)
        self.wait.until(expected_conditions.presence_of_element_located(self.ADDRESS_INPUT))

    def read_current_email(self) -> TempEmail:
        address = self.wait.until(self.read_address)
        return TempEmail(address=address)

    def read_inbox(self) -> list[InboxItem]:
        raise NotImplementedError

    def read_message(self, message_id: str) -> EmailMessage | None:
        raise NotImplementedError

    def request_new_email(self) -> TempEmail:
        raise NotImplementedError

    def read_address(self, driver: WebDriver) -> str:
        element = driver.find_element(*self.ADDRESS_INPUT)
        return (element.get_attribute('value') or '').strip()
