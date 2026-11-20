from datetime import datetime, UTC
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.enum import PurchaseStatus
from src.database.models import Purchases, PurchaseItems
from src.modules.purchases.schema import PurchaseRequest, PurchaseItemRequest


class PurchaseRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, params: list[PurchaseRequest], org_id: UUID, user_id: UUID) -> Purchases:
        purchase = Purchases(
            organization_id=org_id,
            created_by=user_id,
            status=PurchaseStatus.DRAFT,
            items=[
                PurchaseItems(
                    ingredient_id=item.ingredient_id,
                    quantity=item.quantity,
                )
                for item in params
            ],
        )

        self.session.add(purchase)

        await self.session.flush()

        await self.session.refresh(purchase)

        return purchase

    async def get_purchase(self, org_id: UUID, purchase_id: UUID, for_update: bool = False) -> Purchases | None:
        stmt = (
            select(Purchases).where(
                Purchases.id == purchase_id,
                Purchases.organization_id == org_id
            )
            .options(selectinload(Purchases.items))
        )

        if for_update:
            stmt.with_for_update()

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_purchases(self, org_id: UUID) -> list[Purchases]:
        purchases = await self.session.execute(
            select(Purchases).where(Purchases.organization_id == org_id)
            .order_by(Purchases.status)
        )

        return list(purchases.scalars().all())

    async def receive(self, purchase_id: UUID, organization_id: UUID) -> Purchases:
        result = await self.session.execute(
            update(Purchases)
            .where(Purchases.id == purchase_id, Purchases.organization_id == organization_id)
            .values(status=PurchaseStatus.RECEIVED, received_at=datetime.now(UTC))
            .returning(Purchases)
        )

        return result.scalar_one()

    async def cancel(self, purchase_id: UUID, organization_id: UUID) -> Purchases:
        result = await self.session.execute(
            update(Purchases)
            .where(Purchases.id == purchase_id, Purchases.organization_id == organization_id)
            .values(status=PurchaseStatus.CANCELED, cancelled_at=datetime.now(UTC))
            .returning(Purchases)
        )

        return result.scalar_one()

    def replace_items(self, purchase: Purchases, items: list[PurchaseItemRequest]) -> None:
        existing = {item.ingredient_id: item for item in purchase.items}
        updated_items = []

        for item in items:
            row = existing.get(item.ingredient_id)
            if row is None:
                row = PurchaseItems(ingredient_id=item.ingredient_id)

            row.quantity = item.quantity
            row.unit_price = item.unit_price
            updated_items.append(row)

        purchase.items = updated_items
