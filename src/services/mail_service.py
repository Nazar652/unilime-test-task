import logging

from kink import inject

from src.domain.exceptions import MessageNotFoundError
from src.domain.models import EmailMessage, InboxItem, TempEmail
from src.domain.ports import AbstractMailClient

logger = logging.getLogger(__name__)


class MailService:
    @inject
    def __init__(self, client: AbstractMailClient) -> None:
        self.client = client

    def get_email(self) -> TempEmail:
        logger.info('current email requested')
        return self.client.get_current_email()

    def list_inbox(self) -> list[InboxItem]:
        logger.info('inbox listing requested')
        return self.client.fetch_inbox()

    def get_message(self, message_id: str) -> EmailMessage:
        logger.info('message requested: %s', message_id)
        message = self.client.fetch_message(message_id)
        if message is None:
            raise MessageNotFoundError(f'Message {message_id} not found')
        return message

    def refresh_email(self) -> TempEmail:
        logger.info('email refresh requested')
        return self.client.generate_new_email()
