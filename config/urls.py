from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("apps.properties.urls")),
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    path("bookings/", include("apps.bookings.urls", namespace="bookings")),
    prefix_default_language=False,
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
