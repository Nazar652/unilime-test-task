import logging

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from src.domain.exceptions import (
    MailboxTimeoutError,
    MailError,
    MessageNotFoundError,
    ProviderUnavailableError,
)

logger = logging.getLogger('tempmail.errors')


def init_app(app: Flask) -> None:
    @app.errorhandler(MessageNotFoundError)
    def on_message_not_found(error: MessageNotFoundError):
        logger.warning('message not found: %s', error)
        return jsonify(error=str(error) or 'Message not found'), 404

    @app.errorhandler(MailboxTimeoutError)
    def on_timeout(error: MailboxTimeoutError):
        logger.error('provider timed out: %s', error, exc_info=error)
        return jsonify(error=str(error) or 'Provider timed out'), 504

    @app.errorhandler(ProviderUnavailableError)
    def on_provider_unavailable(error: ProviderUnavailableError):
        logger.error('provider unavailable: %s', error, exc_info=error)
        return jsonify(error=str(error) or 'Provider unavailable'), 502

    @app.errorhandler(MailError)
    def on_mail_error(error: MailError):
        logger.error('mail service error: %s', error, exc_info=error)
        return jsonify(error=str(error) or 'Mail service error'), 503

    @app.errorhandler(Exception)
    def on_unexpected(error: Exception):
        if isinstance(error, HTTPException):
            return error
        logger.error('unexpected error: %s', error, exc_info=error)
        return jsonify(error='Internal server error'), 500
