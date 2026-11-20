# Contributing

Thanks for helping make the AI Automation Starter Kit more useful to Python developers.

## Before opening an issue

- Check existing issues and discussions for a similar request.
- Include your Python version, operating system, the install profile(s) used, and the full error output when reporting an installation problem.
- For package requests, explain the common use case and why it belongs in a profile.

## Development setup

Use Python 3.11 or newer, then run from the repository root:

```bash
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -e ".[openai,server,dev]"
ruff check .
ruff format --check .
pytest
```

## Pull request guidelines

- Keep the base install empty and keep specialized tools optional.
- Prefer actively maintained packages with clear use cases and reasonable Python/platform support.
- Do not add exact version pins to `pyproject.toml`; this project resolves current compatible versions at installation time.
- Put heavyweight or platform-sensitive dependencies in their own profile and document their footprint.
- When changing extras, update the README profile table and tests.
- Run the CI commands locally and describe any dependency trade-offs in the PR.

By submitting a contribution, you agree that it may be distributed under this project's MIT license.
