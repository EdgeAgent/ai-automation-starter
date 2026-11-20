from __future__ import annotations

import tomllib
from pathlib import Path

import ai_automation_starter

ROOT = Path(__file__).resolve().parents[1]


def read_project() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as project_file:
        return tomllib.load(project_file)["project"]


def test_package_version_matches_project_metadata() -> None:
    project = read_project()
    assert project["version"] == "0.2.0"
    assert ai_automation_starter.__version__ == project["version"]


def test_project_requires_supported_python() -> None:
    assert read_project()["requires-python"] == ">=3.11"


def test_default_install_includes_the_core_foundation_and_cli() -> None:
    project = read_project()
    assert {"pydantic", "httpx", "python-dotenv", "packaging"} <= set(project["dependencies"])
    assert project["scripts"]["ai-starter"] == "ai_automation_starter.cli:app"
    assert "core" not in project["optional-dependencies"]


def test_openai_example_has_a_focused_provider_extra() -> None:
    extras = read_project()["optional-dependencies"]
    assert extras["openai"] == ["openai"]


def test_all_contains_expected_runtime_tools_but_not_heavy_ml_or_dev() -> None:
    extras = read_project()["optional-dependencies"]
    all_packages = set(extras["all"])
    expected = {"fastapi", "openai", "playwright", "pandas", "chromadb", "pypdf"}
    assert expected <= all_packages
    assert "torch" not in all_packages
    assert "pytest" not in all_packages


def test_every_project_requirement_is_unpinned() -> None:
    project = read_project()
    packages_by_profile = {"default": project["dependencies"], **project["optional-dependencies"]}
    for profile, packages in packages_by_profile.items():
        for package in packages:
            assert not any(operator in package for operator in ("==", "~=", ">", "<")), (
                f"{profile} unexpectedly pins or constrains {package}"
            )
