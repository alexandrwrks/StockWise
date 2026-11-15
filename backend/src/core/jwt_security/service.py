from datetime import timedelta, datetime, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status
from pydantic import ValidationError

from src.core.jwt_security.schema import TokenData, TokenType
from src.core.settings import settings


class JWTSecurity:
    def __init__(self):
        self.ALGORITHM = settings.ALGORITHM
        self.ACCESS_TOKEN_MINUTES = settings.ACCESS_TOKEN_MINUTES
        self.REFRESH_TOKEN_DAYS = settings.REFRESH_TOKEN_DAYS
        self.SECRET_API_KEY = settings.SECRET_API_KEY

    def _create_token(self, data: TokenData, token_type: TokenType, time_delta: timedelta) -> str:
        payload = {
            "user_id": str(data.user_id),
            "role": data.role.value,
            "organization_id": str(data.organization_id),
            "token_type": token_type.value,
            "exp": datetime.now(timezone.utc) + time_delta,
            "iat": datetime.now(timezone.utc),
        }

        return jwt.encode(
            payload=payload,
            key=self.SECRET_API_KEY,
            algorithm=self.ALGORITHM
        )

    def create_access_token(self, data: TokenData) -> str:
        return self._create_token(data=data, token_type=TokenType.ACCESS, time_delta=timedelta(minutes=self.ACCESS_TOKEN_MINUTES))

    def create_refresh_token(self, data: TokenData) -> str:
        return self._create_token(data=data, token_type=TokenType.REFRESH, time_delta=timedelta(days=self.REFRESH_TOKEN_DAYS))

    def _verify_token(self, token: str):
        try:
            payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_API_KEY,
            algorithms=[self.ALGORITHM],
            options={
                "require": [
                    "exp", "iat", "user_id",
                    "organization_id", "role", "token_type",
                ],
                },
            )

            TokenData.model_validate(payload)

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Истёкший токен"
            )

        except (jwt.InvalidTokenError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            )

    def verify_token_type(self, payload: dict[str, Any], token_type: TokenType) -> dict[str, Any]:
        if payload.get("user_id") is None or payload.get("organization_id") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен",
            )

        if payload.get("token_type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена",
            )

        return payload

    def verify_access_token(self, credentials: str) -> dict[str, Any]:
        payload = self._verify_token(credentials)
        return self.verify_token_type(payload, TokenType.ACCESS)

    def verify_refresh_token(self, credentials: str) -> dict[str, Any]:
        payload = self._verify_token(credentials)
        return self.verify_token_type(payload, TokenType.REFRESH)


jwt_service = JWTSecurity()
