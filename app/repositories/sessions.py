class SessionRepository:
    def __init__(self, db):
        self.db = db

    def create(self, user_id, token_hash, remember_me, created_at, expires_at):
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO user_sessions (
                    user_id, session_token_hash, remember_me, created_at, expires_at
                )
                VALUES (%s,%s,%s,%s,%s)
                """,
                (user_id, token_hash, remember_me, created_at, expires_at),
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    def get_active_by_hash(self, token_hash, now):
        return self.db.fetch_one(
            """
            SELECT id, user_id, remember_me, created_at, expires_at, revoked_at
            FROM user_sessions
            WHERE session_token_hash = %s
              AND revoked_at IS NULL
              AND expires_at > %s
            LIMIT 1
            """,
            (token_hash, now),
        )

    def revoke_by_hash(self, token_hash, revoked_at):
        conn = self.db.connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE user_sessions
                SET revoked_at = %s
                WHERE session_token_hash = %s
                  AND revoked_at IS NULL
                """,
                (revoked_at, token_hash),
            )
            conn.commit()
        finally:
            conn.close()
