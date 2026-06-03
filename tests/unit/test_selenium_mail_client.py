from unittest.mock import MagicMock, Mock

import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException

from src.clients.pages.inbox_page import InboxPage
from src.clients.selenium_mail_client import SeleniumMailClient
from src.config import Config
from src.domain.exceptions import MailboxTimeoutError, ProviderUnavailableError
from src.domain.models import EmailMessage, InboxItem, TempEmail


def make_client(monkeypatch) -> SeleniumMailClient:
    return SeleniumMailClient(MagicMock(), Config())


def test_get_current_email_returns_address(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.read_current_email.return_value = TempEmail(address='a@b.com')
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    assert client.get_current_email() == TempEmail(address='a@b.com')
    page.open.assert_called_once_with()
    page.read_current_email.assert_called_once_with()


def test_get_current_email_translates_timeout(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.open.side_effect = TimeoutException('slow')
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    with pytest.raises(MailboxTimeoutError):
        client.get_current_email()


def test_get_current_email_translates_webdriver_error(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.open.side_effect = WebDriverException('boom')
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    with pytest.raises(ProviderUnavailableError):
        client.get_current_email()


def test_fetch_inbox_returns_items(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    items = [InboxItem(id='1', sender='a@b.com', subject='hi', received_at='t')]
    page.read_inbox.return_value = items
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    assert client.fetch_inbox() == items
    page.open.assert_called_once_with()
    page.read_inbox.assert_called_once_with()


def test_fetch_inbox_translates_timeout(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.open.side_effect = TimeoutException('slow')
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    with pytest.raises(MailboxTimeoutError):
        client.fetch_inbox()


def test_fetch_message_returns_message(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    message = EmailMessage(id='x', sender='a', subject='s', received_at='t', body='b')
    page.read_message.return_value = message
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    assert client.fetch_message('x') == message
    page.read_message.assert_called_once_with('x')


def test_fetch_message_returns_none_when_missing(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.read_message.return_value = None
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    assert client.fetch_message('missing') is None


def test_fetch_message_translates_webdriver_error(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.read_message.side_effect = WebDriverException('boom')
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    with pytest.raises(ProviderUnavailableError):
        client.fetch_message('x')


def test_generate_new_email_returns_address(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.request_new_email.return_value = TempEmail(address='new@host.com')
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    assert client.generate_new_email() == TempEmail(address='new@host.com')
    page.open.assert_called_once_with()
    page.request_new_email.assert_called_once_with()


def test_generate_new_email_translates_timeout(monkeypatch):
    client = make_client(monkeypatch)
    page = Mock()
    page.open.side_effect = TimeoutException('slow')
    monkeypatch.setattr(client, 'inbox_page', Mock(return_value=page))

    with pytest.raises(MailboxTimeoutError):
        client.generate_new_email()


def test_inbox_page_built_on_live_driver(monkeypatch):
    client = make_client(monkeypatch)
    driver = Mock()
    client.browser.get_driver.return_value = driver

    page = client.inbox_page()

    assert isinstance(page, InboxPage)
    assert page.driver is driver
    assert page.config is client.config
