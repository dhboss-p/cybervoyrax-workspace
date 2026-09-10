from datetime import datetime, timedelta, timezone

from flask import current_app

from .errors import AuthenticationError
from .security import (
    generate_session_token,
    hash_token,
    verify_password,
)
from .validation import normalize_email


class AuthService:
    def __init__(self, user_repository, session_repository):
        self.users = user_repository
        self.sessions = session_repository

    def authenticate(self, email, password, remember_me=False, session_token=None):
        email = normalize_email(email)
        record = self.users.get_auth_record_by_email(email)

        if not record:
            raise AuthenticationError("No workspace account was found for that email address.")
        if not verify_password(password, record["password_hash"]):
            raise AuthenticationError("The password for this workspace account is incorrect.")

        if record["account_status"] != "ACTIVE":
            raise AuthenticationError("This account is not currently available.")

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if remember_me:
            expires_at = now + timedelta(
                days=current_app.config["REMEMBER_SESSION_TTL_DAYS"]
            )
        else:
            expires_at = now + timedelta(
                minutes=current_app.config["SESSION_TTL_MINUTES"]
            )

        token = session_token or generate_session_token()
        token_hash = hash_token(token)

        self.sessions.create(
            user_id=record["id"],
            token_hash=token_hash,
            remember_me=remember_me,
            created_at=now,
            expires_at=expires_at,
        )

        return token, expires_at

    def resolve_session(self, raw_token):
        if not raw_token:
            return None

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        session_row = self.sessions.get_active_by_hash(hash_token(raw_token), now)

        if not session_row:
            return None

        return self.users.get_by_id(session_row["user_id"])

    def logout(self, raw_token):
        if not raw_token:
            return

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        self.sessions.revoke_by_hash(hash_token(raw_token), now)

    def verify_reauthentication(self, user_id, password):
        user = self.users.get_by_id(user_id)
        if not user:
            raise AuthenticationError("Account not found.")

        auth_record = self.users.get_auth_record_by_email(user.email)

        if not auth_record or not verify_password(password, auth_record["password_hash"]):
            raise AuthenticationError("Password confirmation failed.")

        return True
