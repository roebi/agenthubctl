from pathlib import Path

import connexion
from starlette.responses import HTMLResponse

from agenthubctl.domain.models import StatusValue
from agenthubctl.domain.ports import AgentStatusPort, AgentTerminalAccessPort

_SPEC_PATH = Path(__file__).parent / "openapi.json"
_DASHBOARD_PATH = Path(__file__).parent.parent / "dashboard" / "static" / "index.html"

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
    _status_port.report(name, StatusValue(body["status"]), message=body.get("message"))
    return None, 204


def get_agent_terminal(name: str):
    url = _terminal_port.resolve(name)
    if url is None:
        raise connexion.ProblemException(status=404, title="Agent terminal not found")
    return {"url": url}


def create_app(status_port: AgentStatusPort, terminal_port: AgentTerminalAccessPort | None):
    global _status_port, _terminal_port
    _status_port = status_port
    _terminal_port = terminal_port

    app = connexion.AsyncApp(__name__)
    app.add_api(_SPEC_PATH)
    app.add_url_rule("/", view_func=_serve_dashboard)
    return app


async def _serve_dashboard(request):
    return HTMLResponse(_DASHBOARD_PATH.read_text())
