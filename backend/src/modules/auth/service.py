from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import password_security
from src.modules.auth.repo import AuthRepo
from src.modules.auth.schema import RegisterRequest, RegisterResponse, LoginRequest


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
        except SQLAlchemyError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка регистрации пользователя"
            )

        return RegisterResponse.model_validate(new_user)

    async def login(self, params: LoginRequest):
        exists_user = await self.repo.get_user_by_email(params.email)
        if exists_user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Почта ещё не была зарегистрирована"
            )

        if not password_security.verify_password(params.password, exists_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="НЕверный пароль"
            )

        return RegisterResponse.model_validate(exists_user)

    async def me(self, user_id: UUID) -> RegisterResponse:
        user = await self.repo.get_user_by_uuid(user_id)
        if user is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователя не существует"
            )

        return RegisterResponse.model_validate(user)