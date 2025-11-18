from typing import ClassVar

from django.core.validators import MinValueValidator
from django.db import models


class Room(models.Model):
    description = models.TextField()
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Цена за ночь в основной валюте.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar[tuple[str, ...]] = ("id",)

    def __str__(self) -> str:  # pragma: no cover
        return f"Room #{self.pk}"


class Booking(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    date_start = models.DateField()
    date_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering: ClassVar[tuple[str, ...]] = ("date_start", "id")
        indexes: ClassVar[tuple[models.Index, ...]] = (
            models.Index(fields=["room", "date_start"]),
            models.Index(fields=["room", "date_end"]),
        )

    def __str__(self) -> str:  # pragma: no cover
        return f"Booking #{self.pk}"
