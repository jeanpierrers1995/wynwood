from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone",
        "country",
        "preferred_language",
        "is_staff",
        "is_active",
        "date_joined",
    )

    list_filter = ("is_staff", "is_active", "preferred_language", "country")
    search_fields = ("email", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            _("Profile"),
            {"fields": ("phone", "country", "preferred_language")},
        ),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            _("Profile"),
            {"fields": ("email", "first_name", "last_name", "phone", "country")},
        ),
    )
