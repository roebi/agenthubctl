from typer.testing import CliRunner

from agenthubctl.cli import app

runner = CliRunner()


def test_cli_help_works():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "status-dir" in result.output


def test_cli_rejects_unexpected_subcommand_name():
    # documents real Typer behavior: a single @app.command() collapses to a
    # default command with no subcommand name - "serve" is NOT a valid word
    # to pass on the command line, unlike architecture.md originally implied
    result = runner.invoke(app, ["serve"])

    assert result.exit_code == 2
