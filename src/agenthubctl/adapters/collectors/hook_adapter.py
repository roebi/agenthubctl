from agenthubctl.domain.models import StatusValue
from agenthubctl.domain.ports import AgentStatusPort

# Claude Code hook events (hook_event_name) and the status each one means.
# Stop fires when the agent has finished its turn; it maps to "done" as in
# requirements.md FR-01. Events not listed here are accepted and ignored.
_STATUS_BY_EVENT = {
    "SessionStart": StatusValue.IDLE,
    "UserPromptSubmit": StatusValue.WORKING,
    "PreToolUse": StatusValue.WORKING,
    "Notification": StatusValue.BLOCKED,
    "Stop": StatusValue.DONE,
}


class HookAdapter:
    def __init__(self, agent_id: str, status_port: AgentStatusPort) -> None:
        self._agent_id = agent_id
        self._status_port = status_port

    def handle_hook_event(self, payload: dict) -> None:
        status = _STATUS_BY_EVENT.get(payload.get("hook_event_name"))
        if status is None:
            return
        # Notification payloads carry the text shown to the user, e.g.
        # "Claude needs your permission to use Bash"
        message = payload.get("message")
        self._status_port.report(
            self._agent_id,
            status,
            message=message if isinstance(message, str) else None,
        )
