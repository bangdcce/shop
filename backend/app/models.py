from decimal import Decimal
from sqlmodel import SQLModel, Field
from pydantic import BaseModel, EmailStr


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(
        max_length=100,
    )
    price: Decimal = Field(max_digits=10, decimal_places=2, gt=0)
    stock: int = Field(ge=0)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str
    role: str = Field(default="customer", max_length=20)


class UserIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserOut(BaseModel):
    id: int
    email: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
