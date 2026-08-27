from typer.testing import CliRunner

from agenthubctl.cli import app

runner = CliRunner()


def test_serve_command_exists_and_help_works():
    result = runner.invoke(app, ["serve", "--help"])

    assert result.exit_code == 0
    assert "serve" in result.output.lower()
