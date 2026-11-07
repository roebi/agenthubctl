from datetime import datetime, timezone

import pytest

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


def test_report_when_another_writer_has_a_tmp_file_open_leaves_it_untouched(tmp_path):
    # NFR-04: a concurrent writer's in-progress tmp file for the same agent
    # must never be truncated or renamed into place by this write
    store = FileStatusStore(base_dir=tmp_path)
    other_writers_tmp = tmp_path / "web-dashboard.json.tmp"
    other_writers_tmp.write_text("partial")

    store.report("web-dashboard", StatusValue.WORKING)

    assert other_writers_tmp.read_text() == "partial"


def test_report_with_path_traversal_name_raises_and_writes_nothing(tmp_path):
    base = tmp_path / "status"
    store = FileStatusStore(base_dir=base)

    with pytest.raises(ValueError):
        store.report("../escape", StatusValue.WORKING)

    assert list(tmp_path.rglob("*escape*")) == []


def test_get_with_path_traversal_name_raises(tmp_path):
    store = FileStatusStore(base_dir=tmp_path / "status")

    with pytest.raises(ValueError):
        store.get("../escape")
