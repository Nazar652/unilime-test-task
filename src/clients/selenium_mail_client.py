from kink import inject
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.clients.browser import BrowserSession
from src.clients.pages.inbox_page import InboxPage
from src.config import Config
from src.domain.exceptions import MailboxTimeoutError
from src.domain.models import EmailMessage, InboxItem, TempEmail


class SeleniumMailClient:
    @inject
    def __init__(self, config: Config) -> None:
        self.config = config
        self.browser = BrowserSession(config)

    def get_current_email(self) -> TempEmail:
        with self.browser.lock:
            try:
                page = self.inbox_page()
                page.open()
                return page.read_current_email()
            except TimeoutException as error:
                raise MailboxTimeoutError('Timed out reading the temp email address') from error
            except WebDriverException as error:
                raise MailboxTimeoutError('Could not reach temp-mail.io') from error

    def fetch_inbox(self) -> list[InboxItem]:
        raise NotImplementedError

    def fetch_message(self, message_id: str) -> EmailMessage | None:
        raise NotImplementedError

    def generate_new_email(self) -> TempEmail:
        raise NotImplementedError

    def inbox_page(self) -> InboxPage:
        return InboxPage(self.browser.get_driver(), self.config)
