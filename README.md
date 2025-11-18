# Hotel Booking Service

Простой JSON API на Django/DRF для управления номерами и их бронированиями.
Все ответы в формате JSON, ошибки возвращаются как `{"error": "…"}`.

## Что внутри
- Django 4.2 + DRF
- PostgreSQL 16
- Poetry для зависимостей
- Docker Compose для локального запуска (`infra/docker-compose.yml`)

## Подготовка окружения
1) Скопируйте `.env.example` → `.env` и при необходимости измените
   `DATABASE_URL` или параметры Postgres.

## Запуск через Docker Compose
```bash
docker compose -f infra/docker-compose.yml up --build
```
- Приложение: http://localhost:9000
- База: порт 5432 на хосте (учётка по умолчанию `postgres/postgres`,
  БД `hotel`).
- Статические файлы сохраняются в volume `staticfiles`.

## Локальный запуск без контейнеров
```bash
pip install poetry
poetry install
poetry run python hotel_booking_service/manage.py migrate
poetry run python hotel_booking_service/manage.py runserver 0.0.0.0:9000
```

## API
Все хендлеры не требуют авторизации и принимают JSON или form-data.

**Номера**
- `POST /rooms/create` — создать номер (`description`, `price`), ответ `201`:
  `{"room_id": 1}`.
- `DELETE /rooms/<room_id>/delete` — удалить номер и его брони, ответ
  `200`: `{"room_id": 1}`.
- `GET /rooms/list?order_by=price|created_at&direction=asc|desc` —
  список номеров с сортировкой, ответ `200`: массив объектов.

**Брони**
- `POST /bookings/create` — создать бронь (`room_id`, `date_start`,
  `date_end` в формате `ГГГГ-ММ-ДД`, `date_end ≥ date_start`),
  ответ `201`: `{"booking_id": 10}`. Проверяется пересечение периодов.
- `DELETE /bookings/<booking_id>/delete` — удалить бронь, ответ `200`:
  `{"booking_id": 10}`.
- `GET /bookings/list?room_id=<id>` — список броней номера, отсортированный
  по `date_start`.

## Тесты
```bash
poetry run pytest
```

## Дополнительно
- `infra/schema.sql` — SQL-скрипт создания таблиц `rooms` и `bookings`
  с индексами и ограничениями.
