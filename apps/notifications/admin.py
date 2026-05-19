from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for user notifications."""
    list_display = ("notification_type", "subject", "recipient", "is_read", "sent_at")
    list_filter = ("notification_type", "is_read", "sent_at")
    search_fields = ("subject", "recipient__email", "recipient__first_name")
    date_hierarchy = "sent_at"
    readonly_fields = ("sent_at",)

    ordering = ("-sent_at",)
