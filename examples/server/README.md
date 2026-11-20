# AI job server example

This example is a small but complete vertical slice: a FastAPI API accepts authenticated jobs, Celery runs the OpenAI request in a worker, and Redis brokers jobs and stores their results. It is intended as a starting point, not a finished multi-tenant production service.

## Run locally with Docker Compose

Requirements: Docker Engine with the Docker Compose plugin, an OpenAI API key, and a generated API bearer token.

1. From the repository root, copy `.env.example` to `.env`.
2. Edit `.env`: set `OPENAI_API_KEY` to your provider key, and replace `AI_STARTER_API_TOKEN` with a strong random value. To generate one, run:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Never commit `.env` or paste real keys into issues, chat, or logs.
3. Start the API, worker, and Redis:

   ```bash
   docker compose up --build
   ```

4. In another terminal, submit a job. Replace `<your-token>` with the value in `.env`:

   ```bash
   curl -sS http://localhost:8000/v1/jobs \
     -H 'Authorization: Bearer <your-token>' \
     -H 'Content-Type: application/json' \
     -d '{"prompt":"Give me three ideas for automating invoice intake."}'
   ```

   The API returns `202 Accepted` and a `job_id`. Poll its status:

   ```bash
   curl -sS http://localhost:8000/v1/jobs/<job-id> \
     -H 'Authorization: Bearer <your-token>'
   ```

   A successful response contains `status: "succeeded"` and the model output. The API docs are at `http://localhost:8000/docs`; liveness and Redis readiness checks are `/healthz` and `/readyz`.

Use `docker compose logs -f api worker` to inspect service logs. Stop the stack with `Ctrl+C`, then `docker compose down`. The named Redis volume remains so queued jobs/results are not deleted by a normal stop; remove it only when you intentionally want to discard local Redis data.

## Run without Docker

Install the focused profiles:

```bash
python -m pip install -e ".[openai,server]"
```

Run Redis separately, set the values from `.env.example` in your environment or `.env`, then start the API and worker in separate terminals:

```bash
uvicorn examples.server.app:app --reload
celery -A examples.server.worker.celery_app worker --loglevel=INFO
```

## What the example demonstrates

- Bearer-token protection for job submission and status lookup. The API refuses those routes when `AI_STARTER_API_TOKEN` is missing; it never silently starts with an open job endpoint.
- Prompt validation and asynchronous job submission, so slow provider calls do not hold an HTTP request open.
- Separate liveness (`/healthz`) and Redis readiness (`/readyz`) checks.
- Generic client-facing failure messages; worker exception details stay in server logs.
- Dependency injection in tests, so CI does not require Redis, credentials, or paid model calls.

The sample uses a single shared bearer token. Before a real deployment, add user-level identity and authorization, rate limiting/quotas, request and output retention controls, monitoring, backups, TLS/reverse-proxy configuration, and a tested secret-rotation and rollback process. Review provider costs and data-retention policies before sending user data to a model. Redis and Docker are external services; installing Python packages does not operate or secure them.
