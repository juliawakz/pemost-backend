from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views.choices import RoleChoicesView
from users.views.login import LoginAPIView
from users.views.logout import LogoutView
from users.views.password import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from users.views.profile import ProfileView
from users.views.registration import (
    EExtensionRegistrationView,
    RegisterAccountView,
    SuperExtensionRegistrationView,
    VerifyAccountView,
    AgrodealerRegistrationView
)
from users.views.token import CustomTokenRefreshView, ObtainAuthTokenView
from users.viewset.user import UserViewSet
from users.viewset.work_request import (
    EExtensionWorkRequestViewSet,
    FarmerWorkRequestViewSet,
)
from users.viewset.api_key import ApiKeyViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(
    r"work-requests/e-extension",
    EExtensionWorkRequestViewSet,
    basename="e-extension-work-requests"
)
router.register(
    r"work-requests/farmer",
    FarmerWorkRequestViewSet,
    basename="farmer-work-requests"
)
router.register(r"api-keys", ApiKeyViewSet, basename="api-keys")

urlpatterns = [
    path(
        "apikey/",
        ObtainAuthTokenView.as_view(),
        name='obtain-auth-token'
    ),
    # Farmer/Agrodealer registration
    path(
        "register/",
        RegisterAccountView.as_view(),
        name="register-account"
    ),
    # Role-specific registration endpoints
    path(
        "register/agrodealer/",
        AgrodealerRegistrationView.as_view(),
        name="register-agrodealer"
    ),
    path(
        "register/e-extension/",
        EExtensionRegistrationView.as_view(),
        name="register-e-extension"
    ),
    path(
        "register/super-extension/",
        SuperExtensionRegistrationView.as_view(),
        name="register-super-extension"
    ),
    # Account verification
    path(
        "verify/account/",
        VerifyAccountView.as_view(),
        name="verify-account"
    ),
    path(
        "roles/",
        RoleChoicesView.as_view(),
        name="role-choices"
    ),
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
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

