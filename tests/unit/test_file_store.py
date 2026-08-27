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


def test_get_returns_none_for_unknown_agent(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)

    assert store.get("never-reported") is None


def test_list_returns_all_reported_statuses(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    store.report("web-dashboard", StatusValue.BLOCKED)
    store.report("data-pipeline", StatusValue.WORKING)

    names = {status.name for status in store.list()}

    assert names == {"web-dashboard", "data-pipeline"}


def test_report_leaves_no_leftover_tmp_file(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)

    store.report("web-dashboard", StatusValue.WORKING)

    tmp_files = list(tmp_path.glob("*.tmp"))
    assert tmp_files == []
