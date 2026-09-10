import re
from .errors import ValidationError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def require_text(value, field, min_length=1, max_length=255):
    if not isinstance(value, str):
        raise ValidationError(f"{field} must be text.")

    value = value.strip()

    if len(value) < min_length:
        raise ValidationError(f"{field} is required.")

    if len(value) > max_length:
        raise ValidationError(f"{field} is too long.")

    return value


def normalize_email(value):
    value = require_text(value, "Email", max_length=150).lower()

    if not EMAIL_RE.match(value):
        raise ValidationError("Enter a valid email address.")

    return value
