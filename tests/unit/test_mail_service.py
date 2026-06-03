from unittest.mock import create_autospec

from src.domain.models import TempEmail
from src.domain.ports import MailClient
from src.services.mail_service import MailService


def test_get_email_returns_address_from_client():
    client = create_autospec(MailClient, instance=True)
    client.get_current_email.return_value = TempEmail(address='abc@necub.com')

    service = MailService(client)

    assert service.get_email() == TempEmail(address='abc@necub.com')
    client.get_current_email.assert_called_once_with()
