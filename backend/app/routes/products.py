from fastapi import APIRouter
from sqlmodel import select

from app.db import SessionDep
from app.models import Product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
def list_products(session: SessionDep):
    return session.exec(select(Product).order_by(Product.price, Product.id)).all()
