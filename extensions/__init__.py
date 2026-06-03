from flask import Flask

from extensions import dependency_injection, error_handlers, logging, router


def init_extensions(app: Flask) -> None:
    logging.init_app(app)
    dependency_injection.init_app()
    error_handlers.init_app(app)
    router.init_app(app)
