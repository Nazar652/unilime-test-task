import logging
from collections.abc import Iterator
from contextlib import contextmanager

from kink import inject
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.clients.browser import BrowserSession
from src.clients.pages.inbox_page import InboxPage
from src.config import Config
from src.domain.exceptions import MailboxTimeoutError, ProviderUnavailableError
from src.domain.models import EmailMessage, InboxItem, TempEmail

logger = logging.getLogger(__name__)


class SeleniumMailClient:
    @inject
    def __init__(self, browser: BrowserSession, config: Config) -> None:
        self.config = config
        self.browser = browser

    def get_current_email(self) -> TempEmail:
        with self.page_session() as page:
            page.open()
            return page.read_current_email()

    def fetch_inbox(self) -> list[InboxItem]:
        with self.page_session() as page:
            page.open()
            return page.read_inbox()

    def fetch_message(self, message_id: str) -> EmailMessage | None:
        with self.page_session() as page:
            return page.read_message(message_id)

    def generate_new_email(self) -> TempEmail:
        with self.page_session() as page:
            page.open()
            return page.request_new_email()

    @contextmanager
    def page_session(self) -> Iterator[InboxPage]:
        with self.browser.lock:
            try:
                yield self.inbox_page()
            except TimeoutException as error:
                logger.warning('Timed out reading the temp email address')
                raise MailboxTimeoutError('Timed out reading the temp email address') from error
            except WebDriverException as error:
                logger.error('browser failure talking to provider: %s', error)
                raise ProviderUnavailableError('Could not reach provider') from error

    def inbox_page(self) -> InboxPage:
        return InboxPage(self.browser.get_driver(), self.config)
