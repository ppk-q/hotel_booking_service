"""Тесты HTTP-слоя API."""

from datetime import date

import pytest
from rest_framework.test import APIClient

from hotel_booking_service.api.models import Booking, Room


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def room() -> Room:
    return Room.objects.create(
        description="Vip room",
        price_per_night="1500.00",
    )


@pytest.mark.django_db
def test_room_created(api_client: APIClient):
    payload = {"description": "Стандарт", "price": "2300.50"}

    response = api_client.post("/rooms/create", data=payload, format="json")

    assert response.status_code == 201
    assert "room_id" in response.data
    room = Room.objects.get(pk=response.data["room_id"])
    assert room.description == payload["description"]


@pytest.mark.django_db
def test_room_creation_rejects_negative_price(api_client: APIClient):
    response = api_client.post(
        "/rooms/create",
        data={"description": "Номер", "price": "-1"},
        format="json",
    )

    assert response.status_code == 400
    assert response.data["error"] == "Цена не может быть отрицательной"


@pytest.mark.django_db
def test_booking_prevents_overlap(api_client: APIClient, room: Room):
    Booking.objects.create(
        room=room,
        date_start=date(2024, 10, 1),
        date_end=date(2024, 10, 5),
    )

    response = api_client.post(
        "/bookings/create",
        data={
            "room_id": room.id,
            "date_start": "2024-10-03",
            "date_end": "2024-10-06",
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "Номер занят на выбранные даты"


@pytest.mark.django_db
def test_booking_list_sorted_by_start(api_client: APIClient, room: Room):
    first = Booking.objects.create(
        room=room,
        date_start=date(2024, 9, 1),
        date_end=date(2024, 9, 5),
    )
    second = Booking.objects.create(
        room=room,
        date_start=date(2024, 8, 25),
        date_end=date(2024, 8, 28),
    )

    response = api_client.get(f"/bookings/list?room_id={room.id}")

    assert response.status_code == 200
    assert [item["booking_id"] for item in response.json()] == [
        second.id,
        first.id,
    ]
