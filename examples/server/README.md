# FastAPI example

This small example demonstrates that the `server` extra installs the dependencies needed to start a Python HTTP API. It is deliberately a liveness endpoint, not a complete application template.

From the repository root:

```bash
python -m pip install -e ".[server]"
uvicorn app:app --app-dir examples/server --reload
```

Visit `http://127.0.0.1:8000/healthz` for the health response and `http://127.0.0.1:8000/docs` for the generated OpenAPI docs.

Before using a service in production, add appropriate authentication and authorization, request validation, rate limits, secure secret handling, TLS/reverse-proxy configuration, database migration and backup procedures, structured error handling, monitoring and alerts, and a tested deployment/rollback process. Do not use `--reload` in production.
