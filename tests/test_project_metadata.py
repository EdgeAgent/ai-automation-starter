from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_project() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as project_file:
        return tomllib.load(project_file)["project"]


def test_project_requires_supported_python() -> None:
    project = read_project()
    assert project["requires-python"] == ">=3.11"


def test_default_install_includes_the_core_foundation() -> None:
    project = read_project()
    assert {"pydantic", "httpx", "python-dotenv"} <= set(project["dependencies"])
    assert "core" not in project["optional-dependencies"]


def test_all_contains_the_expected_runtime_profiles() -> None:
    extras = read_project()["optional-dependencies"]
    all_packages = set(extras["all"])
    expected = {"fastapi", "openai", "playwright", "pandas", "chromadb", "pypdf"}
    assert expected <= all_packages
    assert "torch" not in all_packages
    assert "pytest" not in all_packages


def test_every_profile_package_is_unpinned() -> None:
    project = read_project()
    packages_by_profile = {"default": project["dependencies"], **project["optional-dependencies"]}
    for profile, packages in packages_by_profile.items():
        for package in packages:
            assert not any(operator in package for operator in ("==", "~=", ">", "<")), (
                f"{profile} unexpectedly pins or constrains {package}"
            )
