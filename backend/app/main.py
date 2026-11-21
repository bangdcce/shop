"""main.py: builds the FastAPI app. uvicorn starts it with:  uv run uvicorn app.main:app --reload"""

from fastapi import FastAPI
from sqlmodel import select
from app.db import SessionDep

app = FastAPI(title="Shop API", version="0.1.0")


@app.get("/health")
def health(session: SessionDep):
    """Used by humans, tests, Docker and monitoring: is the API alive, and can it reach the database?"""
    session.exec(select(1))  # cheapest possible question; if the database is down this raises -> 500
    return {"status": "ok", "database": "ok"}


# New routers are plugged in here, for example:
# from app.routes import products
# app.include_router(products.router)
