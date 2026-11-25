# Decisions (ADR-lite)

One line per decision the team makes: date, decision, why.

| Date | Decision | Why |
| --- | --- | --- |
| 20/11/2026 | FastAPI + uv for the backend | the stack the team knows; fast tests with TestClient |
| 20/11/2026 | PostgreSQL from day one (SQLModel + psycopg, Alembic) | same database in dev, test and production; migrations instead of manual changes |
| 20/11/2026 | Hosting: Neon (DB) + Render (API) + Vercel (web) | free tiers; Render free Postgres expires after 30 days, Neon does not |
| 20/11/2026 | Layered architecture (routes / services / models+db), one-way dependencies; move to feature folders at ~4-5 areas | simplest structure that keeps HTTP, business rules and data apart; see docs/architecture.md |
| 25/11/2026 | Hypothesis (property-based test) for the product filter | the machine generates 60 random data sets and compares the API with a simple Python rule; it caught a mutation (`stock >= 0`) that example tests missed |
