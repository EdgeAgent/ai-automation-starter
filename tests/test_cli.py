from typer.testing import CliRunner

from ai_automation_starter.cli import app

runner = CliRunner()


def test_profiles_command_lists_openai_and_server_extras() -> None:
    result = runner.invoke(app, ["profiles"])

    assert result.exit_code == 0
    assert "openai" in result.output
    assert "server" in result.output
    assert ".[openai]" in result.output


def test_doctor_passes_for_installed_default_profile() -> None:
    result = runner.invoke(app, ["doctor", "--profile", "default"])

    assert result.exit_code == 0
    assert "All direct requirements" in result.output


def test_doctor_explains_unknown_profile() -> None:
    result = runner.invoke(app, ["doctor", "--profile", "not-a-profile"])

    assert result.exit_code != 0
    assert "Unknown profile" in result.output
    assert "server" in result.output
