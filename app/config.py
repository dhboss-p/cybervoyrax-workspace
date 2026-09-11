import os
class Config:
    SECRET_KEY=os.getenv("SECRET_KEY","dev-only-change-me")
    MYSQL_HOST=os.getenv("MYSQL_HOST","db")
    MYSQL_PORT=int(os.getenv("MYSQL_PORT","3306"))
    MYSQL_DATABASE=os.getenv("MYSQL_DATABASE","cybervoyrax")
    MYSQL_USER=os.getenv("MYSQL_USER","cybervoyrax")
    MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD","cybervoyrax")
    DB_CONNECT_RETRIES=int(os.getenv("DB_CONNECT_RETRIES","30"))
    DB_CONNECT_RETRY_DELAY=float(os.getenv("DB_CONNECT_RETRY_DELAY","2"))
    SESSION_COOKIE_NAME=os.getenv("SESSION_COOKIE_NAME","cvx_session")
    AUTH_COOKIE_NAME=os.getenv("AUTH_COOKIE_NAME","cybervoyrax_auth")
    SESSION_TTL_MINUTES=int(os.getenv("SESSION_TTL_MINUTES","480"))
    REMEMBER_SESSION_TTL_DAYS=int(os.getenv("REMEMBER_SESSION_TTL_DAYS","14"))
    REAUTH_TTL_MINUTES=int(os.getenv("REAUTH_TTL_MINUTES","10"))
    JWT_TTL_MINUTES=int(os.getenv("JWT_TTL_MINUTES","30"))
    UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER","/workspace/instance/uploads")
    MAX_CONTENT_LENGTH=10*1024*1024
    APP_VERSION="0.6.4-phase6.4"
    APP_PHASE="6.4"


