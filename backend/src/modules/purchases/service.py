from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.enum import PurchaseStatus
from src.modules.ingredients.repo import IngredientRepo
from src.modules.organizations.schema import MemberResponse
from src.modules.purchases.repo import PurchaseRepo
from src.modules.purchases.schema import PurchaseRequest, FullPurchaseResponse, PurchaseResponse, PurchaseUpdate


class PurchaseService:
    def __init__(self, session: AsyncSession):
        self.repo = PurchaseRepo(session)
        self.ingredient_repo = IngredientRepo(session)
        self.db = session

    async def create(self, params: list[PurchaseRequest], member: MemberResponse) -> FullPurchaseResponse:

        if not params:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Закупка должна содержать как минимум одну позицию"
            )

        request_ids = {item.ingredient_id for item in params}

        if len(request_ids) != len(params):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Ингредиенты не должны повторяться"
            )

        try:
            existing_ids = await self.ingredient_repo.get_existing_ids(member.organization_id, request_ids)

            missing_ids = request_ids - existing_ids

            if missing_ids:
                ids = ",".join(sorted(map(str, missing_ids)))
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ингредиенты не найдены в этой организации: {ids}"
                )

            purchase = await self.repo.add(params=params, org_id=member.organization_id, user_id=member.user_id)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return FullPurchaseResponse.model_validate(purchase)

    async def get_purchases(self, org_id: UUID) -> list[PurchaseResponse]:
        try:
            purchases = await self.repo.get_purchases(org_id)

        except Exception:
            await self.db.rollback()
            raise

        return [
            PurchaseResponse.model_validate(purchase)
            for purchase in purchases
        ]

    async def get_purchase(self, org_id: UUID, purchase_id: UUID) -> FullPurchaseResponse:
        try:
            purchase = await self.repo.get_purchase(purchase_id, org_id)
            if not purchase:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Такого заказа не существует"
                )

        except Exception:
            await self.db.rollback()
            raise

        return FullPurchaseResponse.model_validate(purchase)

    async def receive(self, purchase_id: UUID, organization_id: UUID) -> PurchaseResponse:
        try:
            purchase = await self.repo.get_purchase(purchase_id, organization_id)
            if purchase is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Закупка не найдена"
                )

            if purchase.status in (PurchaseStatus.RECEIVED, PurchaseStatus.CANCELED):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Данное действие нельзя совершить"
                )


            purchase = await self.repo.receive(purchase_id, organization_id)

            ingredients = [
                {"id": item.ingredient_id, "quantity": item.quantity}
                for item in purchase.items
            ]

            await self.ingredient_repo.replenishment(ingredients)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return PurchaseResponse.model_validate(purchase)

    async def cancel(self, purchase_id: UUID, organization_id: UUID) -> PurchaseResponse:
        purchase = await self.repo.get_purchase(purchase_id, organization_id)
        if purchase is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Закупка не найдена"
            )

        if purchase.status in (PurchaseStatus.RECEIVED, PurchaseStatus.CANCELED):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Данное действие нельзя совершить"
            )

        try:
            purchase = await self.repo.cancel(purchase_id, organization_id)

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return PurchaseResponse.model_validate(purchase)

    async def update(self, params: PurchaseUpdate, purchase_id: UUID, organization_id: UUID) -> FullPurchaseResponse:
        try:
            purchase = await self.repo.get_purchase(organization_id, purchase_id, for_update=True)
            if purchase is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Закупка не найдена"
                )

            if purchase.status != PurchaseStatus.DRAFT:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Редактировать можно только черновик закупки"
                )

            if params.items is not None:
                request_ids = {item.ingredient_id for item in params.items}
                existing_ids = await self.ingredient_repo.get_existing_ids(organization_id, request_ids)

                if request_ids - existing_ids:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Некоторые ингредиенты не найдены"
                    )

                self.repo.replace_items(purchase, params.items)

            if "comment" in params.model_fields_set:
                purchase.comment = params.comment

            await self.db.flush()

            await self.db.commit()

        except Exception:
            await self.db.rollback()
            raise

        return FullPurchaseResponse.model_validate(purchase)