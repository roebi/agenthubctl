import time
from typing import Callable

from agenthubctl.domain.models import StatusValue
from agenthubctl.domain.ports import AgentStatusPort


class PollAdapter:
    def __init__(
        self,
        agent_id: str,
        check_fn: Callable[[], StatusValue],
        status_port: AgentStatusPort,
        interval_seconds: float = 5,
    ) -> None:
        self._agent_id = agent_id
        self._check_fn = check_fn
        self._status_port = status_port
        self._interval_seconds = interval_seconds

    def run_once(self) -> None:
        status = self._check_fn()
        self._status_port.report(self._agent_id, status)

    def run_forever(self, sleep_fn: Callable[[float], None] = time.sleep) -> None:
        while True:
            self.run_once()
            sleep_fn(self._interval_seconds)
