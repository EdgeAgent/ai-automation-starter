"""Command-line helpers for inspecting and diagnosing installed profiles."""

from __future__ import annotations

from importlib import metadata
from importlib.metadata import PackageNotFoundError

import typer
from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from rich.console import Console
from rich.table import Table
from rich.text import Text

DISTRIBUTION = "ai-automation-starter-kit"
app = typer.Typer(no_args_is_help=True, help="Inspect the AI Automation Starter Kit.")
console = Console()


def _distribution() -> metadata.Distribution:
    return metadata.distribution(DISTRIBUTION)


def _extras() -> list[str]:
    return sorted(_distribution().metadata.get_all("Provides-Extra") or [])


def _requirements_for(profile: str) -> list[str]:
    """Read direct requirements for the default install or one declared extra."""
    distribution = _distribution()
    available = set(_extras())
    if profile != "default" and profile not in available:
        choices = ", ".join(["default", *sorted(available)])
        raise ValueError(f"Unknown profile {profile!r}. Available profiles: {choices}")

    environment = default_environment()
    environment["extra"] = "" if profile == "default" else profile
    requirements: dict[str, str] = {}
    for raw_requirement in distribution.requires or []:
        requirement = Requirement(raw_requirement)
        marker = requirement.marker
        if marker is None or marker.evaluate(environment):
            requirements[canonicalize_name(requirement.name)] = requirement.name
    return [requirements[name] for name in sorted(requirements)]


def _install_command(profile: str) -> str:
    if profile == "default":
        return "python -m pip install -e ."
    return f'python -m pip install -e ".[{profile}]"'


@app.command("profiles")
def list_profiles() -> None:
    """List the default install and optional extras recorded in package metadata."""
    table = Table(title="AI Automation Starter Kit profiles")
    table.add_column("Profile", style="cyan", no_wrap=True)
    table.add_column("Install from the repository root")
    table.add_row("default", Text(_install_command("default")))
    for profile in _extras():
        table.add_row(profile, Text(_install_command(profile)))
    console.print(table)


@app.command()
def doctor(
    profile: str = typer.Option(
        "default",
        "--profile",
        "-p",
        help="Profile to check: default or one of the optional extras.",
    ),
) -> None:
    """Check whether the profile's direct Python dependencies are installed."""
    try:
        requirements = _requirements_for(profile)
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--profile") from exc

    table = Table(title=f"Dependency check: {profile}")
    table.add_column("Package", style="cyan")
    table.add_column("Version")
    table.add_column("Status")
    missing: list[str] = []

    for requirement in requirements:
        try:
            installed_version = metadata.version(requirement)
        except PackageNotFoundError:
            missing.append(requirement)
            table.add_row(requirement, "—", "[red]missing[/red]")
        else:
            table.add_row(requirement, installed_version, "[green]installed[/green]")

    console.print(table)
    if missing:
        console.print(
            f"Missing {len(missing)} direct requirement(s): {', '.join(missing)}",
            style="yellow",
        )
        console.print(
            f"From the repository root, run: {_install_command(profile)}",
            markup=False,
        )
        raise typer.Exit(code=1)
    console.print("All direct requirements for this profile are installed.", style="green")


@app.command()
def version() -> None:
    """Print the installed starter-kit version."""
    console.print(_distribution().version)
