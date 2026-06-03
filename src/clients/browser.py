import logging
import threading

from kink import inject
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options

from src.config import Config

logger = logging.getLogger(__name__)


class BrowserSession:
    @inject
    def __init__(self, config: Config) -> None:
        self.config = config
        self.driver: webdriver.Chrome | None = None
        self.lock = threading.Lock()

    def get_driver(self) -> webdriver.Chrome:
        driver = self.driver

        if driver is None or not self.is_alive(driver):
            if driver is not None:
                logger.warning('browser session was stale, rebuilding driver')
            driver = self.build_driver()
            self.driver = driver

        return driver

    def quit(self) -> None:
        if self.driver is not None:
            logger.info('closing browser session')
            try:
                self.driver.quit()
            finally:
                self.driver = None

    def build_driver(self) -> webdriver.Chrome:
        logger.info('building chrome driver (headless=%s)', self.config.headless)
        options = Options()
        if self.config.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280,1024')
        options.add_argument('--lang=en-US')
        options.page_load_strategy = 'eager'

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(self.config.page_load_timeout)
        return driver

    @staticmethod
    def is_alive(driver: webdriver.Chrome) -> bool:
        try:
            _ = driver.current_url
            return True
        except WebDriverException:
            return False
