from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.jwt_security.schema import TokensResponse
from src.core.jwt_security.service import jwt_service
from src.core.security import password_security
from src.core.tokens import hash_token
from src.modules.auth.repo import AuthRepo
from src.modules.auth.schema import RegisterRequest, RegisterResponse, LoginRequest, UserDataResponse, UpdateRequest


class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = AuthRepo(session)
        self.db = session

    async def register(self, params: RegisterRequest) -> RegisterResponse:
        exists_user = await self.repo.get_user_by_email(params.email)
        if exists_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Почта уже занята"
            )

        hash_password = password_security.hash_password(params.password)

        try:
            new_user = await self.repo.register(params, hash_password)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return RegisterResponse.model_validate(new_user)

    async def login(self, params: LoginRequest) -> TokensResponse:
        exists_user = await self.repo.get_user_by_email(params.email)
        if exists_user is None or not password_security.verify_password(params.password, exists_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )

        tokens = jwt_service.create_tokens(exists_user.id)
        new_refresh_payload = jwt_service.verify_refresh_token(tokens.refresh_token)
        expires_at = datetime.fromtimestamp(new_refresh_payload["exp"], tz=timezone.utc)

        try:
            await self.repo.add_refresh_token(
                token_hash=hash_token(tokens.refresh_token),
                user_id=exists_user.id,
                expires_at=expires_at
            )

            await self.db.commit()

        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка авторизации"
            )

        return tokens

    async def me(self, user: UserDataResponse) -> UserDataResponse:
        return user

    async def change_password(self, new_password: str, user_id: UUID) -> UserDataResponse:
        hash_password = password_security.hash_password(new_password)
        try:
            user = await self.repo.change_password(hash_password, user_id)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return UserDataResponse.model_validate(user)
    async def update_data(self, params: UpdateRequest, user_id: UUID) -> UserDataResponse:
        data = params.model_dump(exclude_none=True, exclude_unset=True)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нет данных для обновления"
            )

        try:
            user = await self.repo.update_data(data, user_id)

            await self.db.commit()

        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Указанный email уже занят"
            )

        except Exception:
            await self.db.rollback()
            raise

        return UserDataResponse.model_validate(user)

    async def refresh(self, refresh_token: str) -> TokensResponse:
        refresh_payload = jwt_service.verify_refresh_token(refresh_token)

        user_id = UUID(refresh_payload["user_id"])

        old_token_hash = hash_token(refresh_token)

        tokens = jwt_service.create_tokens(user_id)
        new_refresh_payload = jwt_service.verify_refresh_token(tokens.refresh_token)
        expires_at = datetime.fromtimestamp(new_refresh_payload["exp"], tz=timezone.utc)

        try:
            token_id = await self.repo.update_token(
                user_id=user_id,
                old_token_hash=old_token_hash,
                new_token_hash=hash_token(tokens.refresh_token),
                expires_at=expires_at
            )

            if token_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return tokens

    async def logout(self, refresh_token: str) -> None:
        jwt_service.verify_refresh_token(refresh_token)
        try:
            await self.repo.logout(hash_token(refresh_token))

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise