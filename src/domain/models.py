from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TempEmail:
    address: str


@dataclass(frozen=True, slots=True)
class InboxItem:
    id: str
    sender: str
    subject: str
    received_at: str


@dataclass(frozen=True, slots=True)
class EmailMessage:
    id: str
    sender: str
    subject: str
    received_at: str
    body: str
