from dataclasses import asdict
from uuid import UUID

from flask import Response, jsonify
from flask.views import MethodView
from kink import inject

from src.services import MailService


class EmailView(MethodView):
    @inject
    def get(self, service: MailService) -> Response:
        return jsonify(asdict(service.get_email()))


class InboxView(MethodView):
    @inject
    def get(self, service: MailService) -> Response:
        return jsonify([asdict(item) for item in service.list_inbox()])


class MessageView(MethodView):
    @inject
    def get(self, message_id: UUID, service: MailService) -> Response:
        return jsonify(asdict(service.get_message(str(message_id))))


class RefreshEmailView(MethodView):
    @inject
    def post(self, service: MailService) -> Response:
        return jsonify(asdict(service.refresh_email()))
