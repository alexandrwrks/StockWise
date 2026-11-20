from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from src.database.enum import IngredientUnit


class IngredientRequest(BaseModel):
    name: str = Field(..., description="Название ингредиента")
    sku: str = Field(..., description="Артикул - понятный человеку внутренний код ингредиента.")
    unit: IngredientUnit = Field(..., description="Единица измерения товара (ml, gr, pcs)")
    unit_price: Decimal = Field(description="Цена за единицу")
    minimum_stock: Decimal = Field(..., ge=0, description="Минимальный остаток")
    current_stock: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        max_digits=12,
        decimal_places=3,
        description="Начальный остаток ингредиента",
    )
    reorder_lead_time_days: int = Field(
        ..., ge=0, description="Количество дней на получения товара от поставщика"
    )


class IngredientResponse(IngredientRequest):
    id: UUID = Field(..., description="Внутренний UUID товара")
    current_stock: Decimal = Field(..., description="Количество ингредиента в единицах unit")
    unit_price: Decimal | None = Field(description="Цена за единицу")
    is_active: bool = Field(..., description="Используется ли ингредиент сейчас")

    model_config = ConfigDict(from_attributes=True)

class UpdateIngredientRequest(BaseModel):
    name: str | None = Field(default=None, description="Название ингредиента")
    unit_price: Decimal | None = Field(default=None, description="Цена за единицу")
    sku: str | None = Field(
        default=None, description="Артикул - понятный человеку внутренний код ингредиента."
    )
    reorder_lead_time_days: int | None = Field(
        default=None, description="Количество дней на получения товара от поставщика"
    )
