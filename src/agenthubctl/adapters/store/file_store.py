import json
import os
from datetime import datetime, timezone
from pathlib import Path

from agenthubctl.domain.models import AgentStatus, StatusValue


class FileStatusStore:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, agent_id: str) -> Path:
        return self._base_dir / f"{agent_id}.json"

    def report(
        self,
        agent_id: str,
        status: StatusValue,
        message: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        record = AgentStatus(
            name=agent_id,
            status=status,
            timestamp=timestamp or datetime.now(timezone.utc),
            message=message,
        )
        target = self._path_for(agent_id)
        tmp = target.with_suffix(".json.tmp")
        tmp.write_text(record.model_dump_json())
        os.replace(tmp, target)

    def get(self, agent_id: str) -> AgentStatus | None:
        path = self._path_for(agent_id)
        if not path.exists():
            return None
        return AgentStatus.model_validate_json(path.read_text())

    def list(self) -> list[AgentStatus]:
        return [
            AgentStatus.model_validate_json(p.read_text())
            for p in sorted(self._base_dir.glob("*.json"))
        ]
