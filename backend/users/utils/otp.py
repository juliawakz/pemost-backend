import random
import string

from django.utils.crypto import get_random_string


class OtpUtils:
    def generate_security_code(self, token_length):
        return get_random_string(token_length, allowed_chars="0123456789")

    def generate_random_password(self, length=10):
        # Select characters
        letters = random.choices(string.ascii_letters, k=8)
        digits = random.choices(string.digits, k=2)
        special = random.choice(string.punctuation)

        # Combine
        password_list = letters + digits + [special]

        # Shuffle to avoid predictable positions
        random.shuffle(password_list)

        # Join into final password
        password = ''.join(password_list)
        return password
