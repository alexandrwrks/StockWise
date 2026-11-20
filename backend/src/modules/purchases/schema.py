from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator, ConfigDict

from src.database.enum import PurchaseStatus


class PurchaseItemRequest(BaseModel):
    ingredient_id: UUID
    quantity: Decimal = Field(gt=0, max_digits=12, decimal_places=3)
    unit_price: Decimal = Field(gt=0, max_digits=12, decimal_places=3)


class PurchaseRequest(BaseModel):
    ingredient_id: UUID
    quantity: Decimal = Field(gt=0, max_digits=12, decimal_places=3, description="Количество ингредиентов")

class PurchaseResponse(BaseModel):
    id: UUID
    status: PurchaseStatus
    comment: str | None = Field(default=None, max_length=1000)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PurchaseItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingredient_id: UUID
    quantity: Decimal
    unit_price: Decimal | None

class FullPurchaseResponse(BaseModel):
    id: UUID = Field(description="Уникальный UUID закупки")
    status: PurchaseStatus
    comment: str | None = Field(default=None, max_length=1000)
    created_by: UUID = Field(description="Пользователь который создал данную закупку")
    created_at: datetime
    items: list[PurchaseItemResponse] = Field(description="Позиции закупки")

    model_config = ConfigDict(from_attributes=True)

class PurchaseUpdate(BaseModel):
    comment: str | None = Field(default=None, max_length=1000)
    items: list[PurchaseItemRequest] | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_items(self) -> "PurchaseUpdate":
        if "items" in self.model_fields_set and self.items is None:
            raise ValueError("Список позиций не может быть null")

        if self.items is not None:
            ingredients_ids = [item.ingredient_id for item in self.items]

            if len(ingredients_ids) != len(set(ingredients_ids)):
                raise ValueError("Ингредиенты не должны повторяться")

        return self

    # Понадобится exclude_unset=True