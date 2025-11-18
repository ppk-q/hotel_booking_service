from django.urls import path

from api import views

urlpatterns = [
    path("rooms/create", views.RoomCreateView.as_view(), name="room-create"),
    path(
        "rooms/<int:room_id>/delete",
        views.RoomDeleteView.as_view(),
        name="room-delete",
    ),
    path("rooms/list", views.RoomListView.as_view(), name="room-list"),
    path(
        "bookings/create",
        views.BookingCreateView.as_view(),
        name="booking-create",
    ),
    path(
        "bookings/<int:booking_id>/delete",
        views.BookingDeleteView.as_view(),
        name="booking-delete",
    ),
    path(
        "bookings/list",
        views.BookingListView.as_view(),
        name="booking-list",
    ),
]
