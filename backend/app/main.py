"""main.py: builds the FastAPI app. uvicorn starts it with:  uv run uvicorn app.main:app --reload"""
from fastapi import FastAPI

app = FastAPI(title="Shop API", version="0.1.0")


@app.get("/health")
def health():
    """Used by humans, tests, Docker and monitoring to ask: is the API alive?"""
    return {"status": "ok"}


# New routers are plugged in here, for example:
# from app.routes import products
# app.include_router(products.router)
