# Shop

An e-commerce web app: FastAPI (Python) backend, React + TypeScript frontend (later), tests with pytest and Playwright.

## Run the API
```powershell
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```
Docs page: http://127.0.0.1:8000/docs

## Run the tests
```powershell
cd backend
uv run pytest -q
```

## Folders
```
backend/
  app/
    main.py        builds the app, plugs in the routers
    routes/        one file per area (products.py, auth.py, orders.py ...): HTTP only
    (more folders come with the tickets: models, services, domain, db)
  tests/           one test file per area
docs/              architecture.md (why the code is organised this way), decisions.md
```
