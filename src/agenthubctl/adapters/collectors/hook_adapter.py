from agenthubctl.domain.models import StatusValue
from agenthubctl.domain.ports import AgentStatusPort


class HookAdapter:
    def __init__(self, agent_id: str, status_port: AgentStatusPort) -> None:
        self._agent_id = agent_id
        self._status_port = status_port

    def handle_hook_event(self, payload: dict) -> None:
        if payload.get("hook_event_name") == "Notification":
            self._status_port.report(self._agent_id, StatusValue.BLOCKED)
