from pathlib import Path

import connexion

from agenthubctl.domain.ports import AgentStatusPort, AgentTerminalAccessPort

_SPEC_PATH = Path(__file__).parent / "openapi.json"

_status_port: AgentStatusPort | None = None
_terminal_port: AgentTerminalAccessPort | None = None


def list_agents():
    return [s.model_dump(mode="json") for s in _status_port.list()]


def get_agent(name: str):
    status = _status_port.get(name)
    if status is None:
        raise connexion.ProblemException(status=404, title="Agent not found")
    return status.model_dump(mode="json")


def report_agent_status(name: str, body: dict):
    raise NotImplementedError


def get_agent_terminal(name: str):
    raise NotImplementedError


def create_app(status_port: AgentStatusPort, terminal_port: AgentTerminalAccessPort | None):
    global _status_port, _terminal_port
    _status_port = status_port
    _terminal_port = terminal_port

    app = connexion.AsyncApp(__name__)
    app.add_api(_SPEC_PATH)
    return app
