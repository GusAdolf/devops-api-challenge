from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import _used_jti, app

client = TestClient(app)


def setup_function() -> None:
    _used_jti.clear()


def make_token(jti: str | None = None, secret: str = "change-me-in-production") -> str:
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": "test-client",
            "jti": jti or str(uuid.uuid4()),
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )


def auth_headers(token: str | None = None) -> dict[str, str]:
    settings = get_settings()
    return {
        "X-Parse-REST-API-Key": settings.api_key,
        "X-JWT-KWY": token or make_token(),
    }


def test_post_devops_returns_expected_message() -> None:
    response = client.post(
        "/DevOps",
        headers=auth_headers(),
        json={
            "message": "This is a test",
            "to": "Juan Perez",
            "from": "Rita Asturia",
            "timeToLifeSec": 45,
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Hello Juan Perez your message will be sent"}


def test_rejects_invalid_api_key() -> None:
    response = client.post(
        "/DevOps",
        headers={"X-Parse-REST-API-Key": "wrong", "X-JWT-KWY": make_token()},
        json={
            "message": "This is a test",
            "to": "Juan Perez",
            "from": "Rita Asturia",
            "timeToLifeSec": 45,
        },
    )

    assert response.status_code == 401


def test_rejects_reused_jwt() -> None:
    token = make_token()
    payload = {
        "message": "This is a test",
        "to": "Juan Perez",
        "from": "Rita Asturia",
        "timeToLifeSec": 45,
    }

    first = client.post("/DevOps", headers=auth_headers(token), json=payload)
    second = client.post("/DevOps", headers=auth_headers(token), json=payload)

    assert first.status_code == 200
    assert second.status_code == 401


def test_unsupported_methods_return_error() -> None:
    response = client.get("/DevOps")

    assert response.status_code == 200
    assert response.text == "ERROR"
