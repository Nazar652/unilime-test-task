import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Config:
    base_url: str = os.getenv('TEMPMAIL_BASE_URL', 'https://temp-mail.io/en')
    headless: bool = os.getenv('TEMPMAIL_HEADLESS', 'true').lower() == 'true'
    page_load_timeout: int = int(os.getenv('TEMPMAIL_PAGE_LOAD_TIMEOUT', '30'))
    wait_timeout: int = int(os.getenv('TEMPMAIL_WAIT_TIMEOUT', '15'))
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_json: bool = os.getenv('LOG_JSON', 'false').lower() == 'true'
