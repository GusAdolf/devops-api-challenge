from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, model_validator

from app.config import Settings, get_settings

app = FastAPI(title="DevOps Exercise API", version="1.0.0")

_used_jti: set[str] = set()


class DevOpsRequest(BaseModel):
    message: str = Field(min_length=1)
    to: str = Field(min_length=1)
    from_: str = Field(min_length=1)
    time_to_life_sec: int = Field(gt=0)

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, data: object) -> object:
        if isinstance(data, dict):
            normalized = data.copy()
            if "from" in normalized:
                normalized["from_"] = normalized.pop("from")
            if "timeToLifeSec" in normalized:
                normalized["time_to_life_sec"] = normalized.pop("timeToLifeSec")
            return normalized
        return data


class DevOpsResponse(BaseModel):
    message: str


def _validate_jwt(token: str, settings: Settings) -> None:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "jti"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT",
        ) from exc

    jti = str(payload["jti"])
    if jti in _used_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT already used",
        )
    _used_jti.add(jti)


def authorize_request(
    settings: Annotated[Settings, Depends(get_settings)],
    x_parse_rest_api_key: Annotated[str | None, Header()] = None,
    x_jwt_kwy: Annotated[str | None, Header()] = None,
) -> None:
    if x_parse_rest_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    if not x_jwt_kwy:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing JWT",
        )
    _validate_jwt(x_jwt_kwy, settings)


@app.api_route("/DevOps", methods=["GET", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def unsupported_devops_method() -> PlainTextResponse:
    return PlainTextResponse("ERROR")


@app.post("/DevOps", response_model=DevOpsResponse, dependencies=[Depends(authorize_request)])
async def devops(payload: DevOpsRequest) -> DevOpsResponse:
    return DevOpsResponse(message=f"Hello {payload.to} your message will be sent")
