# Decisions (ADR-lite)

One line per decision the team makes: date, decision, why.

| Date | Decision | Why |
| --- | --- | --- |
| 20/11/2026 | FastAPI + uv for the backend | the stack the team knows; fast tests with TestClient |
| 20/11/2026 | PostgreSQL from day one (SQLModel + psycopg, Alembic) | same database in dev, test and production; migrations instead of manual changes |
| 20/11/2026 | Hosting: Neon (DB) + Render (API) + Vercel (web) | free tiers; Render free Postgres expires after 30 days, Neon does not |
