from unittest.mock import MagicMock, Mock, PropertyMock, call

from selenium.common.exceptions import WebDriverException

from src.clients.browser import BrowserSession
from src.config import Config


def make_session(**overrides) -> BrowserSession:
    return BrowserSession(Config(**overrides))


def test_get_driver_builds_when_missing(monkeypatch):
    session = make_session()
    built = Mock()
    monkeypatch.setattr(session, 'build_driver', Mock(return_value=built))

    assert session.get_driver() is built
    assert session.driver is built


def test_get_driver_reuses_live_driver(monkeypatch):
    session = make_session()
    existing = Mock()
    session.driver = existing
    monkeypatch.setattr(session, 'is_alive', Mock(return_value=True))
    build = Mock()
    monkeypatch.setattr(session, 'build_driver', build)

    assert session.get_driver() is existing
    build.assert_not_called()


def test_get_driver_rebuilds_stale_driver(monkeypatch):
    session = make_session()
    session.driver = Mock()
    fresh = Mock()
    monkeypatch.setattr(session, 'is_alive', Mock(return_value=False))
    monkeypatch.setattr(session, 'build_driver', Mock(return_value=fresh))

    assert session.get_driver() is fresh


def test_quit_closes_and_clears_driver():
    session = make_session()
    driver = Mock()
    session.driver = driver

    session.quit()

    driver.quit.assert_called_once_with()
    assert session.driver is None


def test_quit_without_driver_is_noop():
    session = make_session()

    session.quit()

    assert session.driver is None


def test_is_alive_true_when_reachable():
    driver = Mock()
    driver.current_url = 'https://tempail.com/ua/'

    assert BrowserSession.is_alive(driver) is True


def test_is_alive_false_when_session_dead():
    driver = MagicMock()
    type(driver).current_url = PropertyMock(side_effect=WebDriverException('dead'))

    assert BrowserSession.is_alive(driver) is False


def test_build_driver_applies_headless_and_timeout(monkeypatch):
    chrome_cls = Mock()
    options = Mock()
    monkeypatch.setattr('src.clients.browser.webdriver.Chrome', chrome_cls)
    monkeypatch.setattr('src.clients.browser.Options', Mock(return_value=options))
    session = make_session(headless=True, page_load_timeout=42)

    driver = session.build_driver()

    assert driver is chrome_cls.return_value
    chrome_cls.assert_called_once_with(options=options)
    driver.set_page_load_timeout.assert_called_once_with(42)
    assert call('--headless=new') in options.add_argument.call_args_list


def test_build_driver_skips_headless_when_disabled(monkeypatch):
    options = Mock()
    monkeypatch.setattr('src.clients.browser.webdriver.Chrome', Mock())
    monkeypatch.setattr('src.clients.browser.Options', Mock(return_value=options))
    session = make_session(headless=False)

    session.build_driver()

    assert call('--headless=new') not in options.add_argument.call_args_list
