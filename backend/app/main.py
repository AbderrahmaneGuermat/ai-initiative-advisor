"""FastAPI application entry point.

Skeleton stage. This module wires up the app and mounts the router. It contains
no business logic, and it will not gain any: under the method this project
follows, advisory judgement lives in prompt files rather than in Python. See
docs/architecture.md.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import APP_VERSION, settings

app = FastAPI(
    title="AI Initiative Advisor",
    version=APP_VERSION,
    description=(
        "Backend for a strategy-consulting application that helps managers prioritise "
        "enterprise AI initiatives. Skeleton stage: the health endpoint is the only "
        "working capability."
    ),
)

# In normal development the Vite dev server proxies /api, so browser requests
# are same-origin and this middleware is not exercised. It is here for the case
# where the frontend is pointed at the backend directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
