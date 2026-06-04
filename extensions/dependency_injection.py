from kink import di

from src.clients.browser import BrowserSession
from src.clients.selenium_mail_client import SeleniumMailClient
from src.config import Config
from src.domain.ports import AbstractMailClient
from src.services import MailService


def init_app() -> None:
    di[Config] = Config()
    di[BrowserSession] = lambda container: BrowserSession()  # type: ignore
    di[AbstractMailClient] = lambda container: SeleniumMailClient()  # type: ignore
    di[MailService] = lambda container: MailService()  # type: ignore


def get_service[T](alias: type[T]) -> T:
    return di[alias]
