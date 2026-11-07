import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

# Agent names become file names in the status store and path segments in the
# HTTP API, so they are restricted to a safe charset: no "/", no leading ".",
# bounded length. The same pattern is enforced in api/openapi.json.
AGENT_NAME_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"
_AGENT_NAME_RE = re.compile(AGENT_NAME_PATTERN)


def is_valid_agent_name(name: str) -> bool:
    return _AGENT_NAME_RE.fullmatch(name) is not None


class StatusValue(str, Enum):
    WORKING = "working"
    BLOCKED = "blocked"
    IDLE = "idle"
    DONE = "done"


class AgentStatus(BaseModel):
    name: str
    status: StatusValue
    timestamp: datetime
    message: str | None = None
