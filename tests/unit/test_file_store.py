from datetime import datetime, timezone

from agenthubctl.adapters.store.file_store import FileStatusStore
from agenthubctl.domain.models import StatusValue


def test_report_then_get_returns_the_reported_status(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    ts = datetime.now(timezone.utc)

    store.report("web-dashboard", StatusValue.BLOCKED, message="needs deploy approval", timestamp=ts)
    result = store.get("web-dashboard")

    assert result is not None
    assert result.name == "web-dashboard"
    assert result.status == StatusValue.BLOCKED
    assert result.message == "needs deploy approval"
    assert result.timestamp == ts
