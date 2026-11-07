from collections.abc import Callable
from pathlib import Path

import connexion
from connexion.resolver import Resolver
from starlette.responses import HTMLResponse

from agenthubctl.adapters.collectors.hook_adapter import HookAdapter
from agenthubctl.domain.models import StatusValue, is_valid_agent_name
from agenthubctl.domain.ports import AgentStatusPort, AgentTerminalAccessPort

_SPEC_PATH = Path(__file__).parent / "openapi.json"
_DASHBOARD_PATH = Path(__file__).parent.parent / "dashboard" / "static" / "index.html"


def _require_valid_name(name: str) -> None:
    # Connexion already rejects bad names via the spec pattern; this repeats
    # the check so a handler never passes an unchecked name to the store.
    if not is_valid_agent_name(name):
        raise connexion.ProblemException(
            status=400, title="Invalid agent name", detail=repr(name)
        )


def _parse_status(value: object) -> StatusValue:
    try:
        return StatusValue(value)
    except ValueError:
        raise connexion.ProblemException(
            status=400, title="Invalid status", detail=repr(value)
        ) from None


def _make_handlers(
    status_port: AgentStatusPort, terminal_port: AgentTerminalAccessPort
) -> dict[str, Callable]:
    """Build the operation handlers as closures over this app's ports.

    Keeping the ports in closures instead of module globals means every
    create_app() call gets its own independent wiring (no global state).
    Keys are the operationIds in openapi.json.
    """

    def list_agents():
        return [s.model_dump(mode="json") for s in status_port.list()]

    def get_agent(name: str):
        _require_valid_name(name)
        status = status_port.get(name)
        if status is None:
            raise connexion.ProblemException(status=404, title="Agent not found")
        return status.model_dump(mode="json")

    def report_agent_status(name: str, body: dict):
        _require_valid_name(name)
        status = _parse_status(body.get("status"))
        status_port.report(name, status, message=body.get("message"))
        return None, 204

    def report_agent_hook(name: str, body: dict):
        _require_valid_name(name)
        HookAdapter(agent_id=name, status_port=status_port).handle_hook_event(body)
        return None, 204

    def get_agent_terminal(name: str):
        url = terminal_port.resolve(name)
        if url is None:
            raise connexion.ProblemException(
                status=404, title="Agent terminal not found"
            )
        return {"url": url}

    return {
        handler.__name__: handler
        for handler in (
            list_agents,
            get_agent,
            report_agent_status,
            report_agent_hook,
            get_agent_terminal,
        )
    }


def create_app(status_port: AgentStatusPort, terminal_port: AgentTerminalAccessPort):
    handlers = _make_handlers(status_port, terminal_port)

    def resolve_handler(operation_id: str) -> Callable:
        try:
            return handlers[operation_id]
        except KeyError:
            # connexion turns ValueError into a ResolverError at startup
            raise ValueError(f"no handler for operationId {operation_id!r}") from None

    app = connexion.AsyncApp(__name__)
    app.add_api(_SPEC_PATH, resolver=Resolver(function_resolver=resolve_handler))
    app.add_url_rule("/", view_func=_serve_dashboard)
    return app


async def _serve_dashboard(request):
    return HTMLResponse(_DASHBOARD_PATH.read_text())
