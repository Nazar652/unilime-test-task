from unittest.mock import Mock

from src.clients.pages.inbox_page import InboxPage
from src.config import Config
from src.domain.models import TempEmail


def make_page() -> InboxPage:
    return InboxPage(Mock(), Config())


def test_open_navigates_and_waits(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'wait', Mock())

    page.open()

    page.driver.get.assert_called_once_with(page.config.base_url)
    page.wait.until.assert_called_once()


def test_read_current_email_wraps_waited_value(monkeypatch):
    page = make_page()
    wait = Mock()
    wait.until.return_value = 'abc@necub.com'
    monkeypatch.setattr(page, 'wait', wait)

    assert page.read_current_email() == TempEmail(address='abc@necub.com')
    wait.until.assert_called_once_with(page.read_address)


def test_read_address_strips_value():
    page = make_page()
    driver = Mock()
    driver.find_element.return_value.get_attribute.return_value = '  a@b.com  '

    assert page.read_address(driver) == 'a@b.com'


def test_read_address_handles_missing_value():
    page = make_page()
    driver = Mock()
    driver.find_element.return_value.get_attribute.return_value = None

    assert page.read_address(driver) == ''
