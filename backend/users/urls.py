from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from users.views.choices import RoleChoicesView
from users.views.login import LoginAPIView
from users.views.logout import LogoutView
from users.views.password import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from users.views.profile import ProfileView
from users.viewset.user import UserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"", UserViewSet, basename="users")

urlpatterns = [
    path("roles/", RoleChoicesView.as_view(), name="role-choices"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("login/", LoginAPIView.as_view(), name="user-login"),
    path(
        "password/reset/",
        PasswordResetView.as_view(),
        name="password-reset"
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="password-change"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh"
    ),
    path("", include(router.urls)),
]
