# Temp Mail Scraper

Flask-API, що автоматизує тимчасову пошту [temp-mail.io](https://temp-mail.io) через
Selenium і віддає дані як JSON.

## Стек

Python 3.14 · Flask · Selenium (headless Chrome) · kink (DI). Архітектура шарова
(гексагональна): контролери → сервіс → порт `AbstractMailClient` → Selenium-адаптер.

## Запуск

```bash
# через Poetry
poetry install
poetry run python app.py

# або через pip
python -m venv .venv && .venv\Scripts\activate   # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Потрібен встановлений Chrome — драйвер підтягує Selenium Manager автоматично.
Сервер: `http://127.0.0.1:5000`.

## Ендпоінти

| Метод | Шлях | Опис |
|-------|------|------|
| GET | `/api/email` | поточна тимчасова адреса |
| GET | `/api/inbox` | список листів (`id`, `sender`, `subject`, `received_at`) |
| GET | `/api/email/<id>` | повний лист (+ `body`); неіснуючий → 404 |
| POST | `/api/email/refresh` | згенерувати нову адресу |

```bash
curl http://127.0.0.1:5000/api/email
# {"address": "g35p8hd4d7@ozsaip.com"}

curl http://127.0.0.1:5000/api/inbox
# [{"id": "957e51a5-...", "sender": "Іван <ivan@gmail.com>",
#   "subject": "Привіт", "received_at": "2026-06-03T23:17:41"}]

curl http://127.0.0.1:5000/api/email/957e51a5-...
# {"id": "957e51a5-...", "sender": "Іван", "subject": "Привіт",
#  "received_at": "2026-06-03T23:17:41", "body": "текст листа"}

curl -X POST http://127.0.0.1:5000/api/email/refresh
# {"address": "dpwdb7ivt2@yzcalo.com"}
```

Коди помилок: `404` — лист не знайдено, `502` — сайт недоступний, `504` — таймаут,
`503` — інша помилка пошти, `500` — неочікувана помилка.

## Makefile

Найчастіші команди обгорнуто в `make` (повний список — `make help`):

| Команда | Дія |
|---------|-----|
| `make install` / `make install-pip` | залежності через Poetry / pip |
| `make run-poetry` / `make run-pip` | дев-сервер через Poetry / `python app.py` |
| `make run-docker` / `make docker-down` | Docker-стек (nginx + gunicorn) угору / вниз |
| `make test` · `make lint` · `make typecheck` | тести / лінтер / типи |
| `make check` | повний гейт (lint + typecheck + test) |

## Тести

```bash
pytest        # юніт-тести
ruff check .  # лінтер
pyright       # типи
```

## Docker

Прод-збірка: gunicorn (WSGI) за nginx, Chrome усередині образу.

```bash
docker compose up --build
# API доступне на http://localhost:8080/api/email
```

## Нюанси скрапінгу

- `received_at` — абсолютний час із тултіпа сайту (локальна TZ браузера),
  сконвертований у ISO без TZ-суфікса.
- У списку відправник повний (`Ім'я <email>`), у повному листі — лише ім'я
  (так показує сайт).
- `/api/inbox` клікає кожен лист, щоб дістати його реальний `id`, тож на великій
  скриньці працює повільніше.
