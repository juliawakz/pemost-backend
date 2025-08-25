import random
import string

from django.utils.crypto import get_random_string


class OtpUtils:
    def generate_security_code(self, token_length):
        return get_random_string(token_length, allowed_chars="0123456789")

    def generate_random_password(self, length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(length))
        return password
