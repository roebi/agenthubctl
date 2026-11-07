from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse

import typer

from agenthubctl.adapters.store.file_store import FileStatusStore
from agenthubctl.adapters.terminal.ttyd_adapter import TtydTerminalAdapter
from agenthubctl.api.app import create_app
from agenthubctl.domain.models import is_valid_agent_name

_ALLOWED_TERMINAL_SCHEMES = ("http", "https")

app = typer.Typer(
    name="agenthubctl",
    help="Status and terminal-attach control hub for n parallel coding agent containers.",
)


def parse_terminal_endpoints(values: list[str]) -> dict[str, str]:
    """Parse NAME=URL pairs into an agent-name-to-ttyd-URL mapping.

    Only http(s) URLs are accepted: the dashboard opens them in the browser,
    so a javascript: or data: URL would be script injection.
    """
    endpoints: dict[str, str] = {}
    for value in values:
        name, separator, url = value.partition("=")
        if not separator or not is_valid_agent_name(name):
            raise ValueError(
                f"expected NAME=URL with a valid agent name, got {value!r}"
            )
        parsed = urlparse(url)
        if parsed.scheme not in _ALLOWED_TERMINAL_SCHEMES or not parsed.netloc:
            raise ValueError(
                f"terminal URL for {name!r} must be http(s)://host..., got {url!r}"
            )
        endpoints[name] = url
    return endpoints


def build_app(status_dir: Path, terminal_endpoints: dict[str, str]):
    return create_app(
        status_port=FileStatusStore(base_dir=status_dir),
        terminal_port=TtydTerminalAdapter(endpoints=terminal_endpoints),
    )


@app.command()
def serve(
    status_dir: Annotated[
        Path, typer.Option(help="Directory holding one JSON status file per agent.")
    ] = Path("./status"),
    host: Annotated[
        str,
        typer.Option(
            help=(
                "Host to bind the HTTP server to. 'localhost' listens on both "
                "127.0.0.1 and ::1; an empty value listens on every address "
                "(IPv4 and IPv6)."
            )
        ),
    ] = "localhost",
    port: Annotated[int, typer.Option(help="Port to bind the HTTP server to.")] = 8000,
    terminal: Annotated[
        list[str] | None,
        typer.Option(
            "--terminal",
            envvar="AGENTHUBCTL_TERMINALS",
            help=(
                "Agent terminal endpoint as NAME=URL, repeatable, e.g. "
                "--terminal web=http://127.0.0.1:7681. "
                "Via the env var: space-separated NAME=URL pairs."
            ),
        ),
    ] = None,
) -> None:
    """Start the agenthubctl status API and dashboard."""
    try:
        endpoints = parse_terminal_endpoints(terminal or [])
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--terminal") from exc
    build_app(status_dir, endpoints).run(host=host, port=port)


if __name__ == "__main__":
    app()
