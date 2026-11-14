from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.jwt_security.service import jwt_service
from src.database.config import get_async_session
from src.modules.auth.repo import AuthRepo
from src.modules.auth.schema import UserDataResponse
from src.modules.auth.service import AuthService


async def get_auth_service(session: AsyncSession = Depends(get_async_session)) -> AuthService:
    return AuthService(session)

security_bearer = HTTPBearer(scheme_name="Access Security Bearer")

async def get_auth_repo(session: AsyncSession = Depends(get_async_session)) -> AuthRepo:
    return AuthRepo(session)

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
        repo: AuthRepo = Depends(get_auth_repo)
) -> UserDataResponse:
    token = credentials.credentials
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    payload = jwt_service.verify_access_token(token)

    user_id = UUID(payload["user_id"])
    try:
        exists_user = await repo.get_user_by_uuid(user_id)
        if exists_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован")

        return UserDataResponse.model_validate(exists_user)
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка получения пользователя")