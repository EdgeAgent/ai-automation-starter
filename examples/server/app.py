"""Minimal health-check API demonstrating the server install profile."""

from fastapi import FastAPI

app = FastAPI(
    title="AI Automation Service Starter",
    description="A minimal starting point for a Python automation API.",
    version="0.1.0",
)


@app.get("/healthz", tags=["operations"])
def health_check() -> dict[str, str]:
    """Return a lightweight liveness response."""
    return {"status": "ok"}
