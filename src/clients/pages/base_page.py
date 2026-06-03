from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait

from src.config import Config


class BasePage:
    def __init__(self, driver: WebDriver, config: Config) -> None:
        self.driver = driver
        self.config = config
        self.wait = WebDriverWait(driver, config.wait_timeout)
