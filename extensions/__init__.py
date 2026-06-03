from flask import Flask

from extensions import dependency_injection, error_handlers, router


def init_extensions(app: Flask) -> None:
    dependency_injection.init_app()
    error_handlers.init_app(app)
    router.init_app(app)
