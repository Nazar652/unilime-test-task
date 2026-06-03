from kink import di

from src.clients.selenium_mail_client import SeleniumMailClient
from src.config import Config
from src.domain.ports import MailClient
from src.services import MailService


def init_app() -> None:
    di[Config] = Config()
    di[MailClient] = lambda container: SeleniumMailClient()  # type: ignore
    di[MailService] = lambda container: MailService()  # type: ignore


def get_service[T](alias: type[T]) -> T:
    return di[alias]
