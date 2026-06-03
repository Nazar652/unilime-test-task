from typing import Protocol

from src.domain.models import EmailMessage, InboxItem, TempEmail


class MailClient(Protocol):
    def get_current_email(self) -> TempEmail:
        ...

    def fetch_inbox(self) -> list[InboxItem]:
        ...

    def fetch_message(self, message_id: str) -> EmailMessage | None:
        ...

    def generate_new_email(self) -> TempEmail:
        ...
