import logging
import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from agenthubctl.domain.models import AgentStatus, StatusValue, is_valid_agent_name

_log = logging.getLogger(__name__)


class FileStatusStore:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, agent_id: str) -> Path:
        if not is_valid_agent_name(agent_id):
            raise ValueError(f"invalid agent name: {agent_id!r}")
        return self._base_dir / f"{agent_id}.json"

    def report(
        self,
        agent_id: str,
        status: StatusValue,
        message: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        target = self._path_for(agent_id)
        record = AgentStatus(
            name=agent_id,
            status=status,
            timestamp=timestamp or datetime.now(UTC),
            message=message,
        )
        # NFR-04: a unique tmp file per write (never shared between concurrent
        # writers for the same agent), fsynced, then atomically renamed over
        # the target - readers see either the old or the new record, never a
        # partial one.
        fd, tmp_name = tempfile.mkstemp(
            dir=self._base_dir, prefix=f".{agent_id}.", suffix=".tmp"
        )
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(record.model_dump_json())
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.replace(tmp, target)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise

    def get(self, agent_id: str) -> AgentStatus | None:
        path = self._path_for(agent_id)
        if not path.exists():
            return None
        return AgentStatus.model_validate_json(path.read_text())

    def list(self) -> list[AgentStatus]:
        statuses = []
        for path in sorted(self._base_dir.glob("*.json")):
            status = self._read_listed(path)
            if status is not None:
                statuses.append(status)
        return statuses

    def _read_listed(self, path: Path) -> AgentStatus | None:
        # Only files this store could have written are listed: one corrupt
        # or foreign file must not break GET /agents or duplicate an agent.
        if not is_valid_agent_name(path.stem):
            _log.warning("skipping status file with invalid name: %s", path)
            return None
        try:
            status = AgentStatus.model_validate_json(path.read_text())
        except OSError, ValidationError:
            _log.warning("skipping unreadable status file: %s", path)
            return None
        if status.name != path.stem:
            _log.warning("skipping status file naming another agent: %s", path)
            return None
        return status
