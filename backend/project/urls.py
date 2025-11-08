from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path(
        "admin/",
        admin.site.urls
    ),
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema"
    ),
    path(
        "api/v2/users/",
        include("users.urls", namespace="users")
    ),
    path(
        "api/v2/locations/",
        include("locations.urls", namespace="locations")
    ),
    path(
        "api/v2/notifications/",
        include("notifications.urls", namespace="notifications")
    ),
    path(
        "api/v2/app/",
        include("app.urls", namespace="app")
    ),
    path(
        "api/v2/crops/",
        include("crops.urls", namespace="crops")
    ),
    path(
        "api/v2/pest-control/",
        include("pest_control.urls", namespace="pest-control")
    )
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path(
            "",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui"
        ),
        path(
            "redoc/",
            SpectacularRedocView.as_view(),
            name="redoc"
        )
    ]

handler404 = "project.views.handler404"
