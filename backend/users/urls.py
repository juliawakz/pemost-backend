from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views.choices import RoleChoicesView
from users.views.delete_account import DeleteAccountView
from users.views.login import LoginAPIView
from users.views.logout import LogoutView
from users.views.password import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from users.views.profile import ProfileView
from users.views.registration import RegisterAccountView, VerifyAccountView
from users.views.token import CustomTokenRefreshView, ObtainAuthTokenView
from users.views.notification_preferences import (
    NotificationPreferencesView
)

app_name = "users"

router = DefaultRouter()


urlpatterns = [
    # Generate API key endpoint
    path(
        "generate/apikey/",
        ObtainAuthTokenView.as_view(),
        name="register-account"
    ),
    # Account verification
    path(
        "register/account/",
        RegisterAccountView.as_view(),
        name="register-account"
    ),
    # Account verification
    path(
        "verify/account/",
        VerifyAccountView.as_view(),
        name="verify-account"
    ),
    # Profile Management
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile-management"
    ),
    # Delete Account
    path(
        "account/delete/",
        DeleteAccountView.as_view(),
        name="delete-account"
    ),
    # Notification Preferences
    path(
        "notification-preferences/",
        NotificationPreferencesView.as_view(),
        name="notification-preferences"
    ),
    # List Available roles
    path(
        "roles/",
        RoleChoicesView.as_view(),
        name="role-choices"
    ),
    path(
        "login/",
        LoginAPIView.as_view(),
        name="user-login"
    ),
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
    path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token-refresh"
    ),
    path("", include(router.urls)),
]
