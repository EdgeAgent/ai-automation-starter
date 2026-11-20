<p align="center">
  <img src="assets/icon.svg" alt="AI Automation Starter Kit icon" width="88" height="88">
</p>

<h1 align="center">AI Automation Starter Kit</h1>

<p align="center">
  A practical, modular Python foundation for AI automations, agents, APIs, and data workflows.
</p>

<p align="center">
  <img src="assets/banner.svg" alt="AI Automation Starter Kit — Build AI services without rebuilding your Python toolbox" width="100%">
</p>

<p align="center">
  <a href="https://github.com/EdgeAgent/ai-automation-starter/actions/workflows/ci.yml"><img src="https://github.com/EdgeAgent/ai-automation-starter/actions/workflows/ci.yml/badge.svg" alt="GitHub Actions CI"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python 3.11 or newer"></a>
  <a href="https://pypi.org/project/pip/"><img src="https://img.shields.io/badge/Install-pip%20%7C%20uv-0A7BBB?logo=pypi&logoColor=white" alt="Install with pip or uv"></a>
  <img src="https://img.shields.io/badge/Optional%20profiles-11-6554C0" alt="Eleven optional install profiles">
  <img src="https://img.shields.io/badge/Dependencies-Latest%20compatible-0E9F6E" alt="Latest compatible dependencies, resolved at install time">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-2E7D32.svg" alt="MIT License"></a>
</p>

**One Python package. Pick the tools you need.** This repository bundles well-used libraries for building AI-enabled Python projects. Install a focused profile for a lean setup, combine profiles for a service, or install the broad `all` bundle when you want a general-purpose toolbox.

> **Important:** This is a dependency starter kit, not a hosted service or a complete production deployment. It installs Python packages; it does not install or operate Redis, a database server, Docker, Node.js, Ollama, or the browser binaries used by Playwright.

## Why this repository?

- **Start faster:** common API, AI, automation, server, and data dependencies are organized and ready to install.
- **Stay modular:** add only the profiles your project needs instead of pulling in a giant bundle by default.
- **Get current compatible releases:** package versions are intentionally not pinned here; the installer resolves the newest releases compatible with your Python version and platform at install time.
- **Build beyond a notebook:** the `server` profile includes a practical foundation for Python APIs, background jobs, database access, and observability.
- **Keep deployment deliberate:** lock and validate dependencies for each application before deploying it.

## Install profiles

| Profile | Includes | Good for |
| --- | --- | --- |
| **Default install** | Pydantic/settings, dotenv, HTTPX, retries, structured logging, Typer, Rich | Common application foundations; installed with the package itself |
| `providers` | OpenAI, Anthropic, Google GenAI, LiteLLM | Calling model APIs and routing between providers |
| `frameworks` | LangChain, LangGraph, LlamaIndex core | Agent and retrieval framework experiments |
| `automation` | Requests, Beautiful Soup, lxml, Playwright | HTTP jobs, scraping, and browser automation |
| `server` | FastAPI, Uvicorn, Gunicorn, SQLAlchemy, Alembic, Redis client, Celery, metrics, telemetry | APIs and long-running Python services |
| `data` | pandas, Polars, DuckDB, PyArrow | Data ingestion, transformation, and analytics |
| `vector` | Chroma, Qdrant, pgvector, Weaviate clients | Vector search and retrieval integrations |
| `documents` | PDF, Word, Excel, and PowerPoint libraries | Document import/export and processing |
| `workflows` | APScheduler, Prefect | Scheduled and orchestrated Python workflows |
| `all` | Every runtime profile above, including the default foundation, except `dev` and heavyweight `ml` | A broad general-purpose Python toolkit |
| `dev` | pytest, coverage, Ruff, mypy, pre-commit | Developing and checking this repository |
| `ml` | PyTorch, Transformers, Sentence Transformers | Local model and embedding work; may require substantial disk, memory, or hardware support |

The core foundation is installed by default. The other groups are optional extras, so you can add only the tools your project needs.

> The `all` extra is intentionally broad and may resolve hundreds of transitive packages. Use focused extras for most projects; `all` excludes both development-only tools and heavyweight local ML frameworks.

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/EdgeAgent/ai-automation-starter.git
cd ai-automation-starter
```

This repository is private, so your GitHub account must have access to clone it. If you are using the ZIP download, extract it and open a terminal in the repository folder instead.

### 2. Create and activate a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install the starter kit

The simplest installation adds the shared Python foundations:

```bash
python -m pip install -e .
```

For a typical AI-backed web service:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[providers,server]"
```

For browser and web automation:

```bash
python -m pip install -e ".[providers,automation]"
python -m playwright install chromium
```

To install the broad toolbox:

```bash
python -m pip install -e ".[all]"
```

To develop the repository itself:

```bash
python -m pip install -e ".[server,dev]"
python -m pytest
```

On Linux hosts, Playwright may also need operating-system libraries. Consult the [Playwright installation guide](https://playwright.dev/python/docs/intro) for your distribution and deployment image.

### Install with uv

If you use [uv](https://docs.astral.sh/uv/), you can install the repository in editable mode with the same extras:

```bash
uv pip install -e ".[providers,server]"
```

## Run the included server example

The example is intentionally small: it proves the server profile can run an API and gives you a clean place to start.

```bash
python -m pip install -e ".[server]"
uvicorn app:app --app-dir examples/server --reload
```

Then open `http://127.0.0.1:8000/healthz` or the interactive API docs at `http://127.0.0.1:8000/docs`.

See [`examples/server/README.md`](examples/server/README.md) for the example's scope and next steps.

## Using this kit as a server foundation

**Yes, this is a useful starting point for an AI automation server.** The `server` profile gives you Python building blocks for an HTTP API, application configuration, database connections and migrations, background jobs, and observability integrations. Combine it with `providers` to call AI APIs, `automation` for browser jobs, and `data` or `vector` if your application needs them.

It does **not** make the service production-ready by itself. Before exposing an application to users, plan for authentication and authorization, request validation, rate limits, secret management, TLS and a reverse proxy, database backups and migrations, task retries and idempotency, monitoring/alerting, and an update/rollback process. Redis, PostgreSQL, and other infrastructure must be provisioned and secured separately. The `redis` Python dependency is a client library; it does not install a Redis server.

## Keeping dependencies current—and deployable

This project leaves dependency versions unpinned so a fresh install can resolve current releases that support your Python/platform combination. To refresh an existing environment, run:

```bash
python -m pip install --upgrade --upgrade-strategy eager -e ".[providers,server]"
```

Unpinned dependencies are convenient for exploration, but a new release can introduce a breaking change. For an application you deploy, validate upgrades in CI, then create and commit a lock file or pinned requirements set for that application. For example, use `uv lock` to create a lock and `uv lock --upgrade` when you intentionally refresh it. This starter kit itself does not claim that every package combination has been tested together.

## Repository layout

```text
.
├── .github/
│   ├── dependabot.yml       # Weekly dependency update proposals
│   └── workflows/ci.yml     # Test and packaging checks on Python 3.11–3.13
├── assets/                  # Editable SVG icon and README banner
├── examples/server/         # Minimal FastAPI health-check service
├── src/ai_automation_starter/
├── tests/                   # Metadata/profile sanity checks
├── LICENSE
├── pyproject.toml           # Package metadata and optional dependency profiles
└── README.md
```

## Contributing

Issues and pull requests are welcome. Before opening a PR, install the server and development profiles and run:

```bash
python -m pip install -e ".[server,dev]"
ruff check .
ruff format --check .
pytest
```

Please keep the default install lean, put specialized or heavyweight tools in their own profile, and update the profile table and tests when changing package groups. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Repository

The source lives in the private GitHub repository [`EdgeAgent/ai-automation-starter`](https://github.com/EdgeAgent/ai-automation-starter). The project has not been published to PyPI; install it by cloning the repository and using the editable install commands above. GitHub Actions runs CI on pushes and pull requests, while Dependabot proposes weekly dependency updates.

## License

Released under the [MIT License](LICENSE).
