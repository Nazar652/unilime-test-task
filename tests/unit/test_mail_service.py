from unittest.mock import create_autospec

import pytest

from src.domain.exceptions import MessageNotFoundError
from src.domain.models import EmailMessage, InboxItem, TempEmail
from src.domain.ports import AbstractMailClient
from src.services.mail_service import MailService


def test_get_email_returns_address_from_client():
    client = create_autospec(AbstractMailClient, instance=True)
    client.get_current_email.return_value = TempEmail(address='abc@necub.com')

    service = MailService(client)

    assert service.get_email() == TempEmail(address='abc@necub.com')
    client.get_current_email.assert_called_once_with()


def test_list_inbox_returns_items_from_client():
    client = create_autospec(AbstractMailClient, instance=True)
    items = [InboxItem(id='1', sender='a@b.com', subject='hi', received_at='t')]
    client.fetch_inbox.return_value = items

    service = MailService(client)

    assert service.list_inbox() == items
    client.fetch_inbox.assert_called_once_with()


def test_get_message_returns_message_from_client():
    client = create_autospec(AbstractMailClient, instance=True)
    message = EmailMessage(id='x', sender='a@b.com', subject='s', received_at='t', body='b')
    client.fetch_message.return_value = message

    service = MailService(client)

    assert service.get_message('x') == message
    client.fetch_message.assert_called_once_with('x')


def test_get_message_raises_when_not_found():
    client = create_autospec(AbstractMailClient, instance=True)
    client.fetch_message.return_value = None

    service = MailService(client)

    with pytest.raises(MessageNotFoundError):
        service.get_message('missing')


def test_refresh_email_returns_address_from_client():
    client = create_autospec(AbstractMailClient, instance=True)
    client.generate_new_email.return_value = TempEmail(address='new@host.com')

    service = MailService(client)

    assert service.refresh_email() == TempEmail(address='new@host.com')
    client.generate_new_email.assert_called_once_with()
