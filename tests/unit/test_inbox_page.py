from unittest.mock import Mock

from selenium.common.exceptions import TimeoutException

from src.clients.pages.inbox_page import InboxPage
from src.config import Config
from src.domain.models import EmailMessage, InboxItem, TempEmail


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


def test_element_label_prefers_title():
    page = make_page()
    scope = Mock()
    scope.find_element.return_value.get_attribute.return_value = 'Bob <b@x.com>'

    assert page.element_label(scope, InboxPage.ROW_SENDER) == 'Bob <b@x.com>'


def test_element_label_falls_back_to_text():
    page = make_page()
    scope = Mock()
    element = scope.find_element.return_value
    element.get_attribute.return_value = None
    element.text = '  Bob  '

    assert page.element_label(scope, InboxPage.ROW_SENDER) == 'Bob'


def test_message_url_builds_from_base():
    page = make_page()

    assert page.message_url('uuid-1') == 'https://temp-mail.io/en/message/uuid-1'


def test_detail_text_strips():
    page = make_page()
    page.driver.find_element.return_value.text = '  hello  '

    assert page.detail_text(InboxPage.DETAIL_BODY) == 'hello'


def test_harvest_row_builds_item(monkeypatch):
    page = make_page()
    row = Mock()
    monkeypatch.setattr(page, 'element_label', Mock(side_effect=['Bob <b@x.com>', 'Subject']))
    monkeypatch.setattr(page, 'read_absolute_date', Mock(return_value='2026-06-03T23:17:41'))
    monkeypatch.setattr(page, 'open_row', Mock(return_value='uuid-1'))

    item = page.harvest_row(row)

    assert item == InboxItem(
        id='uuid-1',
        sender='Bob <b@x.com>',
        subject='Subject',
        received_at='2026-06-03T23:17:41',
    )
    page.open_row.assert_called_once_with(row)


def test_open_row_extracts_uuid_clicks_and_returns(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'wait', Mock())
    page.driver.current_url = 'https://temp-mail.io/en/message/uuid-9'
    row = Mock()

    message_id = page.open_row(row)

    assert message_id == 'uuid-9'
    row.click.assert_called_once_with()
    page.driver.back.assert_called_once_with()


def test_read_inbox_harvests_each_row(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'wait', Mock())
    monkeypatch.setattr(page, 'wait_for_messages', Mock())
    rows = [Mock(), Mock()]
    page.driver.find_elements.return_value = rows
    monkeypatch.setattr(
        page,
        'harvest_row',
        Mock(side_effect=lambda row: InboxItem(id=str(rows.index(row)), sender='', subject='', received_at='')),
    )

    items = page.read_inbox()

    assert [item.id for item in items] == ['0', '1']


def test_read_inbox_returns_empty_when_no_rows(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'wait', Mock())
    monkeypatch.setattr(page, 'wait_for_messages', Mock())
    page.driver.find_elements.return_value = []

    assert page.read_inbox() == []


def test_read_message_returns_none_when_not_found(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'message_loaded', Mock(return_value=False))

    assert page.read_message('missing') is None
    page.driver.get.assert_called_once_with(page.message_url('missing'))


def test_read_message_builds_message(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'message_loaded', Mock(return_value=True))
    monkeypatch.setattr(page, 'wait', Mock())
    monkeypatch.setattr(page, 'detail_text', Mock(side_effect=['Bob', 'Subj', 'Body']))
    monkeypatch.setattr(page, 'read_absolute_date', Mock(return_value='2026-06-03T23:17:41'))

    message = page.read_message('uuid-1')

    assert message == EmailMessage(
        id='uuid-1',
        sender='Bob',
        subject='Subj',
        received_at='2026-06-03T23:17:41',
        body='Body',
    )


def test_message_loaded_true_when_article_present(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'wait', Mock())
    page.driver.find_elements.return_value = [Mock()]

    assert page.message_loaded('uuid-1') is True


def test_message_loaded_false_when_absent(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'wait', Mock())
    page.driver.find_elements.return_value = []

    assert page.message_loaded('uuid-1') is False


def test_message_loaded_false_on_timeout(monkeypatch):
    page = make_page()
    wait = Mock()
    wait.until.side_effect = TimeoutException('slow')
    monkeypatch.setattr(page, 'wait', wait)
    page.driver.find_elements.return_value = [Mock()]

    assert page.message_loaded('uuid-1') is False


def test_request_new_email_clicks_and_returns_new(monkeypatch):
    page = make_page()
    wait = Mock()
    wait.until.return_value = 'new@host.com'
    monkeypatch.setattr(page, 'wait', wait)
    monkeypatch.setattr(page, 'read_address', Mock(return_value='old@host.com'))

    result = page.request_new_email()

    assert result == TempEmail(address='new@host.com')
    page.driver.find_element.return_value.click.assert_called_once_with()


def test_changed_address_returns_value_when_changed(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'read_address', Mock(return_value='new@host.com'))

    assert page.changed_address(Mock(), 'old@host.com') == 'new@host.com'


def test_changed_address_empty_when_same(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'read_address', Mock(return_value='old@host.com'))

    assert page.changed_address(Mock(), 'old@host.com') == ''


def test_changed_address_empty_when_blank(monkeypatch):
    page = make_page()
    monkeypatch.setattr(page, 'read_address', Mock(return_value=''))

    assert page.changed_address(Mock(), 'old@host.com') == ''


def test_parse_date_converts_pm_to_iso():
    page = make_page()

    assert page.parse_date('6/3/2026, 11:17:41 PM') == '2026-06-03T23:17:41'


def test_parse_date_converts_am_to_iso():
    page = make_page()

    assert page.parse_date('1/9/2026, 12:05:00 AM') == '2026-01-09T00:05:00'


def test_parse_date_returns_raw_on_unknown_format():
    page = make_page()

    assert page.parse_date('just now') == 'just now'


def test_read_absolute_date_hovers_and_parses(monkeypatch):
    page = make_page()
    chain = Mock()
    chain.move_to_element.return_value = chain
    monkeypatch.setattr('src.clients.pages.inbox_page.ActionChains', Mock(return_value=chain))
    wait = Mock()
    wait.until.return_value = Mock(text='6/3/2026, 11:17:41 PM')
    monkeypatch.setattr(page, 'wait', wait)
    monkeypatch.setattr(page, 'parse_date', Mock(return_value='2026-06-03T23:17:41'))

    result = page.read_absolute_date(Mock())

    assert result == '2026-06-03T23:17:41'
    chain.perform.assert_called_once_with()
    page.parse_date.assert_called_once_with('6/3/2026, 11:17:41 PM')
