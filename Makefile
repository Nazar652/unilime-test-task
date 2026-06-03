.PHONY: help install install-pip test lint typecheck format check run-poetry run-pip run-docker docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install      - install dependencies via Poetry"
	@echo "  make install-pip  - install runtime deps via pip (requirements.txt)"
	@echo "  make test         - run unit tests"
	@echo "  make lint         - run ruff linter"
	@echo "  make typecheck    - run pyright"
	@echo "  make format       - format code with ruff"
	@echo "  make check        - lint + typecheck + test (full gate)"
	@echo "  make run-poetry   - run the app via Poetry (dev server)"
	@echo "  make run-pip      - run the app via plain Python (dev server)"
	@echo "  make run-docker   - build & run via Docker (nginx + gunicorn)"
	@echo "  make docker-down  - stop the Docker stack"

install:
	poetry install

install-pip:
	pip install -r requirements.txt

test:
	poetry run pytest

lint:
	poetry run ruff check .

typecheck:
	poetry run pyright

format:
	poetry run ruff format .

check: lint typecheck test

run-poetry:
	poetry run python app.py

run-pip:
	python app.py

run-docker:
	docker compose up --build

docker-down:
	docker compose down
