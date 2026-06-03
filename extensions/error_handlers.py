from flask import Flask, jsonify

from src.domain.exceptions import (
    MailboxTimeoutError,
    MailError,
    MessageNotFoundError,
)


def init_app(app: Flask) -> None:
    @app.errorhandler(MessageNotFoundError)
    def on_message_not_found(error: MessageNotFoundError):
        return jsonify(error=str(error) or "Message not found"), 404

    @app.errorhandler(MailboxTimeoutError)
    def on_timeout(error: MailboxTimeoutError):
        return jsonify(error=str(error) or "Mailbox timed out"), 504

    @app.errorhandler(MailError)
    def on_mail_error(error: MailError):
        return jsonify(error=str(error) or "Mail service error"), 503

    @app.errorhandler(NotImplementedError)
    def on_not_implemented(error: NotImplementedError):
        return jsonify(error="Not implemented"), 501
