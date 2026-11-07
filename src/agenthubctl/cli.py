from pathlib import Path

import typer

from agenthubctl.adapters.store.file_store import FileStatusStore
from agenthubctl.adapters.terminal.ttyd_adapter import TtydTerminalAdapter
from agenthubctl.api.app import create_app

app = typer.Typer(
    name="agenthubctl",
    help="Status and terminal-attach control hub for n parallel coding agent containers.",
)


@app.command()
def serve(
    status_dir: Path = typer.Option(
        Path("./status"), help="Directory holding one JSON status file per agent."
    ),
    host: str = typer.Option("127.0.0.1", help="Host to bind the HTTP server to."),
    port: int = typer.Option(8000, help="Port to bind the HTTP server to."),
) -> None:
    """Start the agenthubctl status API and dashboard."""
    status_port = FileStatusStore(base_dir=status_dir)
    terminal_port = TtydTerminalAdapter(endpoints={})
    connexion_app = create_app(status_port=status_port, terminal_port=terminal_port)
    connexion_app.run(host=host, port=port)


if __name__ == "__main__":
    app()
