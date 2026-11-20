# Changelog

Notable changes to the AI Automation Starter Kit are documented here.

## [0.2.0] - 2026-11-20

### Added

- `ai-starter profiles`, `ai-starter doctor`, and `ai-starter version` commands.
- A focused `openai` extra so the runnable server example need not install every provider client.
- An authenticated FastAPI job API with liveness/readiness routes, queue submission, and safe status polling.
- A Redis-backed Celery worker that calls the OpenAI Responses API outside the HTTP request process.
- Dockerfile, Compose stack, and safe `.env.example` for local API/worker/Redis development.
- Network-free tests using fake queue/provider boundaries.

## [0.1.0] - 2026-11-20

### Added

- Modular optional dependency profiles for core Python foundations, AI providers, frameworks, automation, servers, data, vector stores, documents, workflows, development, and local ML.
- Broad `all` profile for common runtime tooling, excluding heavyweight ML and development-only packages.
- FastAPI health-check example, project metadata tests, CI workflow, Dependabot configuration, and editable SVG branding.
