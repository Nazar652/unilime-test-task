from kink import di

from src.clients.selenium_mail_client import SeleniumMailClient
from src.config import Config
from src.domain.ports import MailClient
from src.services import MailService


def init_app() -> None:
    di[Config] = Config()
    di[MailClient] = lambda di: SeleniumMailClient()
    di[MailService] = lambda di: MailService()


def get_service[T](alias: type[T]) -> T:
    return di[alias]
