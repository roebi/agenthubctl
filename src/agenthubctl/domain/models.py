from datetime import datetime
from enum import Enum

from pydantic import BaseModel


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
