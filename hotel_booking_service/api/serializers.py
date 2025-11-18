from typing import ClassVar

from rest_framework import serializers

from api.models import Booking, Room


class RoomSerializer(serializers.ModelSerializer):
    room_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Room
        fields: ClassVar[tuple[str, ...]] = (
            "room_id",
            "description",
            "price_per_night",
            "created_at",
        )


class BookingSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(source="id", read_only=True)
    room_id = serializers.IntegerField(source="room.id", read_only=True)

    class Meta:
        model = Booking
        fields: ClassVar[tuple[str, ...]] = (
            "booking_id",
            "room_id",
            "date_start",
            "date_end",
            "created_at",
        )
