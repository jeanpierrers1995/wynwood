"""
URL patterns for the bookings app.

Covers the booking creation flow: checkout, payment and confirmation.
"""

from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("checkout/<slug:slug>/", views.CheckoutView.as_view(), name="checkout"),
    path("payment/<int:booking_id>/", views.PaymentView.as_view(), name="payment"),
    path(
        "confirmation/<int:booking_id>/",
        views.ConfirmationView.as_view(),
        name="confirmation",
    ),
    path("my-bookings/", views.MyBookingsView.as_view(), name="my-bookings"),
]
