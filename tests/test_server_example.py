from types import SimpleNamespace

from fastapi.testclient import TestClient
from pydantic import SecretStr

from examples.server.app import create_app
from examples.server.settings import Settings

API_TOKEN = "local-test-token-with-enough-random-looking-characters"


def make_app(*, enqueue_job=None, lookup_job=None, redis_check=None, api_token=API_TOKEN):
    return create_app(
        settings=Settings(
            api_token=SecretStr(api_token) if api_token is not None else None,
            redis_url="redis://test.invalid:6379/0",
        ),
        enqueue_job=enqueue_job or (lambda _prompt: SimpleNamespace(id="job-123")),
        lookup_job=lookup_job or (lambda _job_id: SimpleNamespace(state="PENDING", result=None)),
        redis_check=redis_check or (lambda _url: None),
    )


def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {API_TOKEN}"}


def test_health_endpoint_reports_liveness() -> None:
    response = TestClient(make_app()).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_when_redis_is_unavailable() -> None:
    def unavailable(_url: str) -> None:
        raise ConnectionError("private backend details")

    response = TestClient(make_app(redis_check=unavailable)).get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"detail": "Job queue is unavailable"}


def test_jobs_require_a_valid_bearer_token() -> None:
    response = TestClient(make_app()).post("/v1/jobs", json={"prompt": "hello"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_jobs_are_rejected_if_authentication_is_not_configured() -> None:
    response = TestClient(make_app(api_token=None)).post(
        "/v1/jobs", headers=auth_headers(), json={"prompt": "hello"}
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "API authentication is not configured"}


def test_job_submission_returns_an_accepted_job_id() -> None:
    submitted: list[str] = []

    def enqueue(prompt: str) -> SimpleNamespace:
        submitted.append(prompt)
        return SimpleNamespace(id="job-456")

    response = TestClient(make_app(enqueue_job=enqueue)).post(
        "/v1/jobs", headers=auth_headers(), json={"prompt": "  summarize this  "}
    )

    assert response.status_code == 202
    assert response.json() == {"job_id": "job-456", "status": "queued"}
    assert submitted == ["summarize this"]


def test_job_status_returns_success_output() -> None:
    app = make_app(lookup_job=lambda _job_id: SimpleNamespace(state="SUCCESS", result="done"))

    response = TestClient(app).get("/v1/jobs/job-123", headers=auth_headers())

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job-123",
        "status": "succeeded",
        "output": "done",
        "error": None,
    }


def test_job_failure_does_not_disclose_worker_exception() -> None:
    result = SimpleNamespace(state="FAILURE", result=RuntimeError("secret traceback detail"))
    app = make_app(lookup_job=lambda _job_id: result)

    response = TestClient(app).get("/v1/jobs/job-123", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["error"] == "The job failed; check worker logs for details."
    assert "secret traceback detail" not in response.text


def test_blank_prompts_are_rejected_before_enqueue() -> None:
    response = TestClient(make_app()).post(
        "/v1/jobs", headers=auth_headers(), json={"prompt": "   "}
    )

    assert response.status_code == 422
