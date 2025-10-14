from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException


class AccountNotRegisteredException(APIException):
    status_code = 404
    default_detail = _("Unable to log in with provided credentials.")
    default_code = "non-registered-account"


class AccountDisabledException(APIException):
    status_code = 403
    default_detail = _("User account is disabled. Contact Admin")
    default_code = "account-disabled"


class InvalidCredentialsException(APIException):
    status_code = 400
    default_detail = _("Wrong username or password.")
    default_code = "invalid-credentials"


class InactiveAccountException(APIException):
    status_code = 401
    default_detail = _("Account not activated.")
    default_code = "invalid-credentials"


class InvalidEmailException(APIException):
    status_code = 400
    default_detail = _("User with this email does not exist.")
    default_code = "invalid-email"


class PasswordMismatchException(APIException):
    status_code = 400
    default_detail = _("The two password fields didn't match.")
    default_code = "password-mismatch"


class InvalidCurrentPasswordException(APIException):
    status_code = 400
    default_detail = _("Wrong current password.")
    default_code = "password-mismatch"


class InvalidOTPException(APIException):
    status_code = 400
    default_detail = _("The OTP is invalid or expired.")
    default_code = "invalid-otp"
