import pytest
from typer.testing import CliRunner

from agenthubctl.cli import app, build_app, parse_terminal_endpoints

runner = CliRunner()


def test_cli_help_works():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "status-dir" in result.output


def test_cli_help_documents_terminal_option():
    result = runner.invoke(app, ["--help"])

    assert "--terminal" in result.output


def test_cli_rejects_unexpected_subcommand_name():
    # documents real Typer behavior: a single @app.command() collapses to a
    # default command with no subcommand name - "serve" is NOT a valid word
    # to pass on the command line, unlike architecture.md originally implied
    result = runner.invoke(app, ["serve"])

    assert result.exit_code == 2


def test_cli_with_malformed_terminal_option_exits_with_usage_error(tmp_path):
    result = runner.invoke(
        app, ["--status-dir", str(tmp_path), "--terminal", "no-equals-sign"]
    )

    assert result.exit_code == 2


def test_parse_terminal_endpoints_returns_name_to_url_mapping():
    endpoints = parse_terminal_endpoints(
        ["web-dashboard=http://127.0.0.1:7681", "data-pipeline=https://host:7682/"]
    )

    assert endpoints == {
        "web-dashboard": "http://127.0.0.1:7681",
        "data-pipeline": "https://host:7682/",
    }


@pytest.mark.parametrize(
    "value",
    [
        "no-equals-sign",
        "../escape=http://127.0.0.1:7681",
        "web=javascript:alert(1)",
        "web=http://",
    ],
)
def test_parse_terminal_endpoints_with_invalid_value_raises(value):
    with pytest.raises(ValueError):
        parse_terminal_endpoints([value])


def test_build_app_when_terminal_configured_serves_its_url(tmp_path):
    # FR-08 end to end through the real wiring the CLI uses: a configured
    # endpoint is what the dashboard's attach link opens
    client = build_app(
        tmp_path, {"web-dashboard": "http://127.0.0.1:7681"}
    ).test_client()

    response = client.get("/agents/web-dashboard/terminal")

    assert response.status_code == 200
    assert response.json()["url"] == "http://127.0.0.1:7681"
