import hashlib
import secrets
import string


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_secure_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))
