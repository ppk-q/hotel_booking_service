"""HTTP-хендлеры для работы c номерами и бронями."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import ClassVar

from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Booking, Room
from api.serializers import BookingSerializer, RoomSerializer

DATE_FORMAT = "%Y-%m-%d"


class JsonErrorMixin:
    """Добавляет удобный метод для ответов c ошибками."""

    @staticmethod
    def json_error(message: str, status_code: int) -> Response:
        return Response({"error": message}, status=status_code)


class BaseAPIView(JsonErrorMixin, APIView):
    """Базовый класс, отключающий авторизацию и CSRF."""

    authentication_classes: ClassVar[list] = []
    permission_classes: ClassVar[list] = []


class RoomCreateView(BaseAPIView):
    """Создать номер отеля."""

    def post(self, request: HttpRequest) -> Response:
        description = (request.data.get("description") or "").strip()
        if not description:
            return self.json_error(
                "Нужно передать описание номера",
                status.HTTP_400_BAD_REQUEST,
            )

        raw_price = request.data.get("price")
        try:
            price = Decimal(str(raw_price))
        except (InvalidOperation, TypeError):
            return self.json_error(
                "Цена должна быть числом",
                status.HTTP_400_BAD_REQUEST,
            )

        if price < 0:
            return self.json_error(
                "Цена не может быть отрицательной",
                status.HTTP_400_BAD_REQUEST,
            )

        room = Room.objects.create(
            description=description,
            price_per_night=price,
        )
        return Response({"room_id": room.id}, status=status.HTTP_201_CREATED)


class RoomDeleteView(BaseAPIView):
    """Удалить номер и все бронирования."""

    def delete(self, request: HttpRequest, room_id: int) -> Response:
        try:
            room = Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            return self.json_error(
                "Номер не найден",
                status.HTTP_404_NOT_FOUND,
            )

        room.delete()
        return Response({"room_id": room_id}, status=status.HTTP_200_OK)


class RoomListView(BaseAPIView):
    """Получить список номеров c сортировкой."""

    SORTABLE_FIELDS: ClassVar[dict[str, str]] = {
        "price": "price_per_night",
        "created_at": "created_at",
    }

    def get(self, request: HttpRequest) -> Response:
        order_by = request.GET.get("order_by", "created_at")
        if order_by not in self.SORTABLE_FIELDS:
            return self.json_error(
                "order_by должен быть одним из: price, created_at",
                status.HTTP_400_BAD_REQUEST,
            )

        direction = request.GET.get("direction", "asc").lower()
        if direction not in {"asc", "desc"}:
            return self.json_error(
                "direction должен быть asc или desc",
                status.HTTP_400_BAD_REQUEST,
            )

        sort_field = self.SORTABLE_FIELDS[order_by]
        sort_expression = (
            f"-{sort_field}" if direction == "desc" else sort_field
        )

        rooms = Room.objects.all().order_by(sort_expression, "id")
        data = RoomSerializer(rooms, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class BookingCreateView(BaseAPIView):
    """Создать бронь для существующего номера."""

    def post(self, request: HttpRequest) -> Response:
        room = self._get_room(request.data.get("room_id"))
        if isinstance(room, Response):
            return room

        try:
            date_start = self._parse_date(request.data.get("date_start"))
            date_end = self._parse_date(request.data.get("date_end"))
        except ValueError as exc:
            return self.json_error(str(exc), status.HTTP_400_BAD_REQUEST)

        if date_end < date_start:
            return self.json_error(
                "date_end не может быть раньше date_start",
                status.HTTP_400_BAD_REQUEST,
            )

        has_overlap = (
            Booking.objects.filter(room=room)
            .filter(date_start__lte=date_end, date_end__gte=date_start)
            .exists()
        )
        if has_overlap:
            return self.json_error(
                "Номер занят на выбранные даты",
                status.HTTP_409_CONFLICT,
            )

        booking = Booking.objects.create(
            room=room, date_start=date_start, date_end=date_end
        )
        return Response(
            {"booking_id": booking.id},
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_room(raw_room_id: str | int | None) -> Room | Response:
        if raw_room_id in (None, ""):
            return BookingCreateView.json_error(
                "Нужно передать room_id", status.HTTP_400_BAD_REQUEST
            )

        try:
            room_id = int(raw_room_id)
        except (TypeError, ValueError):
            return BookingCreateView.json_error(
                "room_id должен быть целым числом", status.HTTP_400_BAD_REQUEST
            )

        try:
            return Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            return BookingCreateView.json_error(
                "Номер не найден", status.HTTP_404_NOT_FOUND
            )

    @staticmethod
    def _parse_date(value: str | None):
        if not value:
            raise ValueError(
                "Нужно передать date_start и date_end в формате YYYY-MM-DD"
            )

        try:
            return datetime.strptime(value, DATE_FORMAT).date()
        except (TypeError, ValueError) as exc:  # pragma: no cover
            raise ValueError(
                "Неверный формат даты, ожидается YYYY-MM-DD"
            ) from exc


class BookingDeleteView(BaseAPIView):
    """Удалить конкретную бронь."""

    def delete(self, request: HttpRequest, booking_id: int) -> Response:
        deleted, _ = Booking.objects.filter(pk=booking_id).delete()
        if not deleted:
            return self.json_error(
                "Бронь не найдена",
                status.HTTP_404_NOT_FOUND,
            )
        return Response({"booking_id": booking_id}, status=status.HTTP_200_OK)


class BookingListView(BaseAPIView):
    """Вернуть список броней номера, отсортированный по началу."""

    def get(self, request: HttpRequest) -> Response:
        room = self._get_room_from_query(request)
        if isinstance(room, Response):
            return room

        bookings = room.bookings.all().order_by("date_start", "id")
        data = BookingSerializer(bookings, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_room_from_query(request: HttpRequest) -> Room | Response:
        raw_room_id = request.GET.get("room_id")
        if raw_room_id in (None, ""):
            return BookingListView.json_error(
                "room_id обязателен", status.HTTP_400_BAD_REQUEST
            )

        try:
            room_id = int(raw_room_id)
        except (TypeError, ValueError):
            return BookingListView.json_error(
                "room_id должен быть целым числом", status.HTTP_400_BAD_REQUEST
            )

        try:
            return Room.objects.get(pk=room_id)
        except Room.DoesNotExist:
            return BookingListView.json_error(
                "Номер не найден", status.HTTP_404_NOT_FOUND
            )
