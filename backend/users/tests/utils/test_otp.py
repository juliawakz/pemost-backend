from django.conf import settings
from users.utils.otp import OtpUtils


def test_generate_security_code_default_length():
    token_length = getattr(settings, "TOKEN_LENGTH", 6)
    security_code = OtpUtils().generate_security_code(token_length=token_length)
    assert len(security_code) == settings.TOKEN_LENGTH
