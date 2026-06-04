from abc import ABC, abstractmethod

from src.domain.models import EmailMessage, InboxItem, TempEmail


class AbstractMailClient(ABC):
    @abstractmethod
    def get_current_email(self) -> TempEmail: ...

    @abstractmethod
    def fetch_inbox(self) -> list[InboxItem]: ...

    @abstractmethod
    def fetch_message(self, message_id: str) -> EmailMessage | None: ...

    @abstractmethod
    def generate_new_email(self) -> TempEmail: ...
