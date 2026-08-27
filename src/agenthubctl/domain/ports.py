from datetime import datetime
from typing import Protocol

from agenthubctl.domain.models import AgentStatus, StatusValue


class AgentStatusPort(Protocol):
    def report(
        self,
        agent_id: str,
        status: StatusValue,
        message: str | None = None,
        timestamp: datetime | None = None,
    ) -> None: ...

    def get(self, agent_id: str) -> AgentStatus | None: ...

    def list(self) -> list[AgentStatus]: ...


class AgentTerminalAccessPort(Protocol):
    def resolve(self, agent_id: str) -> str | None: ...
