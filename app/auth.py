import hashlib
import hmac
import secrets

from datetime import datetime, timedelta, timezone

import jwt

from fastapi import (
    HTTPException,
    Request,
    status
)

from .config import (
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from .db import user_id


COOKIE = "access_token"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        210000
    )

    return (
        f"pbkdf2_sha256$210000$"
        f"{salt.hex()}$"
        f"{digest.hex()}"
    )


def verify_password(
    password: str,
    encoded_password: str
) -> bool:

    try:
        scheme, rounds, salt, digest = (
            encoded_password.split("$")
        )

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(rounds)
        ).hex()

        return (
            scheme == "pbkdf2_sha256"
            and hmac.compare_digest(
                candidate,
                digest
            )
        )

    except Exception:
        return False


def token(user_id_value: int) -> str:
    expiration = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": str(user_id_value),
        "exp": expiration
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )


def current(request: Request):
    access_token = request.cookies.get(
        COOKIE
    )

    if not access_token:
        return None

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        user_id_value = int(
            payload["sub"]
        )

        return user_id(user_id_value)

    except Exception:
        return None


def set_cookie(
    response,
    access_token: str
):
    response.set_cookie(
        COOKIE,
        access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax"
    )


def require(request: Request):
    user = current(request)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={
                "Location": "/login"
            }
        )

    return user