import json
import logging
import logging.config
import time
import uuid

from flask import Flask, Response, g, has_request_context, request

from src.config import Config

logger = logging.getLogger('tempmail.request')


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'time': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', '-'),
        }
        if record.exc_info:
            payload['exc'] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = current_request_id()
        return True


def current_request_id() -> str:
    if has_request_context():
        return getattr(g, 'request_id', '-')
    return '-'


def new_request_id() -> str:
    return uuid.uuid4().hex[:8]


def elapsed_ms() -> int:
    started: float | int | None = getattr(g, 'request_started', None)
    if started is None:
        return 0
    return int((time.perf_counter() - started) * 1000)


def configure(config: Config) -> None:
    formatter = 'json' if config.log_json else 'plain'
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'request_id': {'()': RequestIdFilter},
        },
        'formatters': {
            'plain': {
                'format': '%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s',
            },
            'json': {
                '()': JsonFormatter,
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
                'formatter': formatter,
                'filters': ['request_id'],
            },
        },
        'root': {
            'level': config.log_level,
            'handlers': ['console'],
        },
    })


def init_app(app: Flask) -> None:
    configure(Config())

    @app.before_request
    def assign_request_id() -> None:
        g.request_id = new_request_id()
        g.request_started = time.perf_counter()

    @app.after_request
    def log_request(response: Response) -> Response:
        logger.info(
            '%s %s -> %s (%s ms)',
            request.method,
            request.path,
            response.status_code,
            elapsed_ms(),
        )
        return response
