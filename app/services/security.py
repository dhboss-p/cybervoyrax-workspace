import hashlib
import secrets
import bcrypt


def verify_password(plain_password, password_hash):
    if not plain_password or not password_hash:
        return False

    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def hash_password(plain_password, rounds=10):
    return bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt(rounds=rounds),
    ).decode("utf-8")


def generate_session_token():
    return secrets.token_urlsafe(48)


def hash_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# Compact JWT helpers used by the local training API.
def _b64url_encode(raw):
    import base64
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

def _b64url_decode(value):
    import base64
    value = value.encode("ascii") if isinstance(value, str) else value
    return base64.urlsafe_b64decode(value + b"=" * (-len(value) % 4))

def issue_workspace_jwt(user_id, role, secret, expires_at):
    import json, hmac
    header = {"typ": "JWT", "alg": "HS256"}
    payload = {"sub": str(user_id), "role": role, "exp": int(expires_at.timestamp())}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url_encode(sig)}"

def resolve_workspace_jwt(token, secret):
    import json, hmac, time
    try:
        h, p, sig = token.split(".")
        header = json.loads(_b64url_decode(h))
        payload = json.loads(_b64url_decode(p))
        alg = str(header.get("alg", "")).lower()
        if alg != "none":
            expected = hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
            supplied = _b64url_decode(sig)
            if not hmac.compare_digest(expected, supplied):
                return None
        if int(payload.get("exp", 0)) <= int(time.time()):
            return None
        return payload
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None
