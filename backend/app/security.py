import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status

from app.config import settings


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Недействительный или истёкший access token") from exc
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Ожидался access token")
    return payload


def new_refresh_token() -> tuple[str, str]:
    raw = secrets.token_urlsafe(48)
    return raw, hash_token(raw)


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def sign_download(attachment_id: int, expires_at: int) -> str:
    payload = f"{attachment_id}.{expires_at}"
    signature = hmac.new(settings.jwt_secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_download(token: str, attachment_id: int) -> None:
    try:
        raw_id, expires_raw, signature = token.split(".", 2)
        if int(raw_id) != attachment_id:
            raise ValueError("id")
        expires_at = int(expires_raw)
    except ValueError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Некорректная ссылка на файл") from exc
    expected = hmac.new(
        settings.jwt_secret.encode(),
        f"{attachment_id}.{expires_at}".encode(),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Подпись ссылки не совпала")
    if datetime.now(timezone.utc).timestamp() > expires_at:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Срок ссылки истёк")
