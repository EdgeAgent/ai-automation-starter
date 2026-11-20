"""Redis-backed Celery worker and example OpenAI task."""

from collections.abc import Callable
from typing import Any

import structlog
from celery import Celery
from openai import OpenAI

from examples.server.settings import Settings

logger = structlog.get_logger(__name__)
settings = Settings()

celery_app = Celery(
    "ai_automation_starter",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    accept_content=["json"],
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    result_serializer="json",
    task_serializer="json",
    task_track_started=True,
    worker_prefetch_multiplier=1,
)


def generate_text(
    prompt: str,
    config: Settings,
    *,
    client_factory: Callable[..., Any] | None = None,
) -> str:
    """Call OpenAI once; client_factory makes the provider boundary easy to test."""
    if config.openai_api_key is None or not config.openai_api_key.get_secret_value():
        raise RuntimeError("OPENAI_API_KEY is not configured for the worker")

    factory = client_factory or OpenAI
    with factory(
        api_key=config.openai_api_key.get_secret_value(),
        timeout=60.0,
        max_retries=2,
    ) as client:
        response = client.responses.create(model=config.model, input=prompt)

    output = response.output_text
    if not output:
        raise RuntimeError("The model returned an empty response")
    return output


@celery_app.task(name="ai_automation_starter.generate_text")
def generate_text_task(prompt: str) -> str:
    """Execute a model call in the worker, not in the API request process."""
    try:
        return generate_text(prompt, settings)
    except Exception as exc:
        logger.exception("ai_job_failed", error_type=type(exc).__name__)
        raise
