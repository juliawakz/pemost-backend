from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from users.views.login import SystemAdminLoginAPIView, UserLoginAPIView
from users.views.logout import LogoutView
from users.views.otp import OtpGenerationView, OtpVerifyOtpView
from users.views.password import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from users.views.profile import ProfileExitsView, ProfileView
from users.views.registration import RegistrationView, UserRegistrationView
from users.viewset.user import UserViewSet

app_name = "users"

router = DefaultRouter()
router.register(r"", UserViewSet, basename="users")

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("register/manager/", UserRegistrationView.as_view(), name="manager-register"),
    path("otp/generate/", OtpGenerationView.as_view(), name="generate-otp"),
    path("otp/verify/", OtpVerifyOtpView.as_view(), name="verify-otp"),
    path("login/", UserLoginAPIView.as_view(), name="user-login"),
    path("login/manager/", SystemAdminLoginAPIView.as_view(), name="manager-login"),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/check-exists/", ProfileExitsView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("", include(router.urls)),
]
