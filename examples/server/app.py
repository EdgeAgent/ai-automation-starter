"""Authenticated AI-job API backed by Redis and a Celery worker."""

from collections.abc import Callable
from secrets import compare_digest
from typing import Any, Literal

import structlog
from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator
from redis import Redis

from examples.server.settings import Settings
from examples.server.worker import celery_app, generate_text_task

logger = structlog.get_logger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)
bearer_dependency = Depends(bearer_scheme)


class JobRequest(BaseModel):
    """Prompt accepted by the asynchronous job endpoint."""

    prompt: str = Field(min_length=1, max_length=8000)

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("prompt must contain non-whitespace text")
        return cleaned


class JobAccepted(BaseModel):
    job_id: str
    status: Literal["queued"] = "queued"


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "succeeded", "failed", "unknown"]
    output: str | None = None
    error: str | None = None


def check_redis(redis_url: str) -> None:
    """Raise when the queue/result backend is not reachable."""
    client = Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
    try:
        client.ping()
    finally:
        client.close()


def require_api_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = bearer_dependency,
) -> None:
    """Require a configured bearer token without disclosing expected credentials."""
    expected = request.app.state.settings.api_token
    if expected is None or not expected.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured",
        )

    supplied = credentials.credentials if credentials is not None else ""
    if credentials is None or not compare_digest(supplied, expected.get_secret_value()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_app(
    *,
    settings: Settings | None = None,
    enqueue_job: Callable[[str], Any] | None = None,
    lookup_job: Callable[[str], Any] | None = None,
    redis_check: Callable[[str], None] | None = None,
) -> FastAPI:
    """Build the API; injectable queue functions keep tests independent of Redis."""
    app = FastAPI(
        title="AI Automation Starter API",
        description="Submit authenticated AI jobs and poll their status.",
        version="0.2.0",
    )
    app.state.settings = settings or Settings()
    app.state.enqueue_job = enqueue_job or generate_text_task.delay
    app.state.lookup_job = lookup_job or (lambda job_id: AsyncResult(job_id, app=celery_app))
    app.state.redis_check = redis_check or check_redis

    @app.get("/healthz", tags=["operations"])
    def liveness() -> dict[str, str]:
        """Report that the API process is responding; does not check dependencies."""
        return {"status": "ok"}

    @app.get("/readyz", tags=["operations"])
    def readiness() -> dict[str, str]:
        """Report readiness only when Redis, the queue/result backend, is reachable."""
        try:
            app.state.redis_check(app.state.settings.redis_url)
        except Exception as exc:
            logger.warning("redis_readiness_check_failed", error_type=type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Job queue is unavailable",
            ) from exc
        return {"status": "ready"}

    @app.post(
        "/v1/jobs",
        response_model=JobAccepted,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["jobs"],
        dependencies=[Depends(require_api_token)],
    )
    def submit_job(payload: JobRequest) -> JobAccepted:
        """Queue a prompt and return immediately with an opaque job identifier."""
        try:
            task = app.state.enqueue_job(payload.prompt)
            job_id = str(task.id)
        except Exception as exc:
            logger.exception("job_enqueue_failed", error_type=type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not enqueue the job",
            ) from exc
        return JobAccepted(job_id=job_id)

    @app.get(
        "/v1/jobs/{job_id}",
        response_model=JobStatus,
        tags=["jobs"],
        dependencies=[Depends(require_api_token)],
    )
    def get_job(job_id: str) -> JobStatus:
        """Return safe job status and output; never expose worker exception details."""
        try:
            result = app.state.lookup_job(job_id)
            state = str(result.state).upper()
        except Exception as exc:
            logger.exception("job_status_lookup_failed", error_type=type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not read job status",
            ) from exc

        if state == "SUCCESS":
            return JobStatus(job_id=job_id, status="succeeded", output=str(result.result or ""))
        if state in {"STARTED", "RETRY"}:
            return JobStatus(job_id=job_id, status="running")
        if state in {"FAILURE", "REVOKED"}:
            return JobStatus(
                job_id=job_id,
                status="failed",
                error="The job failed; check worker logs for details.",
            )
        if state in {"PENDING", "RECEIVED"}:
            return JobStatus(job_id=job_id, status="queued")
        return JobStatus(job_id=job_id, status="unknown")

    return app


app = create_app()
