from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import get_async_session
from src.modules.auth.service import AuthService


async def get_auth_service(session: AsyncSession = Depends(get_async_session)) -> AuthService:
    return AuthService(session)