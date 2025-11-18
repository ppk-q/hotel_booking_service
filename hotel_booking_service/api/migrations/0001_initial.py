# Generated manually for initial schema
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.TextField()),
                (
                    "price_per_night",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Цена за ночь в основной валюте.",
                        max_digits=10,
                        validators=[
                            django.core.validators.MinValueValidator(0)
                        ],
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_start", models.DateField()),
                ("date_end", models.DateField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bookings",
                        to="api.room",
                    ),
                ),
            ],
            options={"ordering": ["date_start", "id"]},
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(
                fields=["room", "date_start"],
                name="api_bookin_room_id_d8f0f0_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="booking",
            index=models.Index(
                fields=["room", "date_end"],
                name="api_bookin_room_id_cc7331_idx",
            ),
        ),
    ]
