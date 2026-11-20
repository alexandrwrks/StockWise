from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    String,
    Numeric,
    Integer,
    Boolean,
    true,
    TIMESTAMP,
    func,
    Enum,
    UniqueConstraint,
    CheckConstraint,
    NUMERIC
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

from src.database.enum import IngredientUnit

from src.database.enum import MemberRole, MemberStatus, PurchaseStatus


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    fullname: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class RefreshTokens(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class OrganizationMembers(Base):
    __tablename__ = "organization_members"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="unique_organization_member",
        ),
    )

    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True, index=True
    )
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole, native_enum=False), nullable=False, default=MemberRole.EMPLOYEE)
    status: Mapped[MemberStatus] = mapped_column(Enum(MemberStatus, native_enum=False), nullable=False, default=MemberStatus.ACTIVE)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Ingredients(Base):
    __tablename__ = "ingredients"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    unit: Mapped[IngredientUnit] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(NUMERIC(12, 3), nullable=True)
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    reorder_lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False)
    current_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=true(), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Organizations(Base):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )

class Purchases(Base):
    __tablename__ = "purchases"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[PurchaseStatus] = mapped_column(
        Enum(PurchaseStatus, name="purchase_status"),
        default=PurchaseStatus.DRAFT,
    )
    comment: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    received_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)

    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    items: Mapped[list["PurchaseItems"]] = relationship(
        back_populates="purchase",
        cascade="all, delete, delete-orphan",
        lazy="selectin",
    )


class PurchaseItems(Base):
    __tablename__ = "purchase_items"

    __table_args__ = (
        UniqueConstraint(
            "purchase_id",
            "ingredient_id",
            name="unique_ingredient_purchase_item",
        ),
    )

    purchase_id: Mapped[UUID] = mapped_column(
        ForeignKey("purchases.id", ondelete="CASCADE"),
        primary_key=True,
    )

    ingredient_id: Mapped[UUID] = mapped_column(
        ForeignKey("ingredients.id"),
        primary_key=True,
        index=True,
    )

    quantity: Mapped[Decimal] = mapped_column(NUMERIC(12, 3))
    unit_price: Mapped[Decimal | None] = mapped_column(NUMERIC(12, 3))

    purchase: Mapped["Purchases"] = relationship(
        back_populates="items",
    )