from kink import inject

from src.domain.models import EmailMessage, InboxItem, TempEmail
from src.domain.ports import MailClient


class MailService:
    @inject
    def __init__(self, client: MailClient) -> None:
        self.client = client

    def get_email(self) -> TempEmail:
        return self.client.get_current_email()

    def list_inbox(self) -> list[InboxItem]:
        raise NotImplementedError

    def get_message(self, message_id: str) -> EmailMessage:
        raise NotImplementedError

    def refresh_email(self) -> TempEmail:
        raise NotImplementedError
