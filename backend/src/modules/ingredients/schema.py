from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from src.databse.enum import IngredientUnit


class IngredientRequest(BaseModel):
    name: str = Field(..., description="Название ингредиента")
    sku: str = Field(..., description="Артикул - понятный человеку внутренний код ингредиента.")
    unit: IngredientUnit = Field(..., description="Единица измерения товара (ml, gr, pcs)")
    minimum_stock: Decimal = Field(..., description="Минимальный остаток")
    reorder_lead_time_days: int = Field(..., description="Количество дней на получения товара от поставщика")


class IngredientResponse(IngredientRequest):
    id: UUID = Field(..., description="Внутренний UUID товара")
    current_stock: Decimal = Field(..., description="Количество ингредиента в единицах unit")
    is_active: bool = Field(..., description="Используется ли ингредиент сейчас")