from decimal import Decimal
from sqlmodel import SQLModel, Field


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        max_length=100,
    )
    price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    stock: int = Field(ge=0)
