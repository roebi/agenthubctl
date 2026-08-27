from typing import Callable

from agenthubctl.domain.models import StatusValue
from agenthubctl.domain.ports import AgentStatusPort


class PollAdapter:
    def __init__(
        self,
        agent_id: str,
        check_fn: Callable[[], StatusValue],
        status_port: AgentStatusPort,
    ) -> None:
        self._agent_id = agent_id
        self._check_fn = check_fn
        self._status_port = status_port

    def run_once(self) -> None:
        status = self._check_fn()
        self._status_port.report(self._agent_id, status)
