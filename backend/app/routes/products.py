from fastapi import APIRouter, HTTPException
from sqlmodel import select
from decimal import Decimal
from app.db import SessionDep
from app.models import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(
    session: SessionDep,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    in_stock: bool = False,
):

    if min_price is not None and max_price is not None and max_price < min_price:
        raise HTTPException(400, "min_price must be <= max_price")
    query = select(Product)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if in_stock == True:
        query = query.where(Product.stock > 0)

    query = query.order_by(Product.price, Product.id)
    return session.exec(query).all()


@router.get("/{product_id}")
def get_product_by_id(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if product is None:
        raise HTTPException(404, "Product not found")
    return product
