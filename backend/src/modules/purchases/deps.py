from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.config import get_async_session
from src.modules.purchases.service import PurchaseService


async def get_purchase_service(session: AsyncSession = Depends(get_async_session)):
    return PurchaseService(session)