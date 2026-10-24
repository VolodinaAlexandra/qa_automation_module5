"""Local helpers for Book Store Login; these are not DemoQA server sources."""
import re


def validate_username(username: str) -> bool:
    if not isinstance(username, str):
        return False
    return bool(username.strip())


def validate_login_password(password: str) -> bool:
    if not isinstance(password, str):
        return False
    return bool(password)


def validate_registration_password(password: str) -> bool:
    if not isinstance(password, str):
        return False
    return bool(re.fullmatch(
        r'(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}',
        password,
    ))


def build_login_payload(username: str, password: str) -> dict:
    if not validate_username(username):
        raise ValueError('Username must not be empty')
    if not validate_login_password(password):
        raise ValueError('Password must not be empty')
    return {'userName': username, 'password': password}


def redact_secrets(value):
    if isinstance(value, dict):
        return {k: '[REDACTED]' if k.lower() in
                {'password', 'token', 'authorization'} else redact_secrets(v)
                for k, v in value.items()}
    if isinstance(value, list):
        return [redact_secrets(v) for v in value]
    return value
