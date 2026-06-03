from flask import Blueprint, Flask

from src.views.email_controller import (
    EmailView,
    InboxView,
    MessageView,
    RefreshEmailView,
)


def init_app(app: Flask) -> None:
    api_router = Blueprint("api", __name__, url_prefix="/api")

    api_router.add_url_rule("/email", view_func=EmailView.as_view("email"))
    api_router.add_url_rule("/inbox", view_func=InboxView.as_view("inbox"))
    api_router.add_url_rule(
        "/email/refresh",
        view_func=RefreshEmailView.as_view("refresh_email"),
    )
    api_router.add_url_rule(
        "/email/<message_id>",
        view_func=MessageView.as_view("message"),
    )

    app.register_blueprint(api_router)
