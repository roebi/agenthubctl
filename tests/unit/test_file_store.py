from datetime import UTC, datetime

import pytest

from agenthubctl.adapters.store.file_store import FileStatusStore
from agenthubctl.domain.models import StatusValue


def test_report_then_get_returns_the_reported_status(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    ts = datetime.now(UTC)

    store.report(
        "web-dashboard",
        StatusValue.BLOCKED,
        message="needs deploy approval",
        timestamp=ts,
    )
    result = store.get("web-dashboard")

    assert result is not None
    assert result.name == "web-dashboard"
    assert result.status == StatusValue.BLOCKED
    assert result.message == "needs deploy approval"
    assert result.timestamp == ts


def test_get_with_unknown_agent_returns_none(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)

    assert store.get("never-reported") is None


def test_list_after_two_reports_returns_both_statuses(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    store.report("web-dashboard", StatusValue.BLOCKED)
    store.report("data-pipeline", StatusValue.WORKING)

    names = {status.name for status in store.list()}

    assert names == {"web-dashboard", "data-pipeline"}


def test_report_when_finished_leaves_no_tmp_file(tmp_path):
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


def test_get_after_restart_returns_the_status_reported_before(tmp_path):
    # FR-04: a new store on the same directory (as after a process restart)
    # sees what the previous one wrote
    FileStatusStore(base_dir=tmp_path).report("web-dashboard", StatusValue.IDLE)

    restarted = FileStatusStore(base_dir=tmp_path)

    assert restarted.get("web-dashboard").status == StatusValue.IDLE


def test_list_when_a_status_file_is_corrupt_skips_it(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    store.report("web-dashboard", StatusValue.WORKING)
    (tmp_path / "broken.json").write_text("{not json")

    assert [s.name for s in store.list()] == ["web-dashboard"]


def test_list_when_a_file_names_another_agent_skips_it(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    store.report("web-dashboard", StatusValue.WORKING)
    impostor = (tmp_path / "web-dashboard.json").read_text()
    (tmp_path / "copy.json").write_text(impostor)

    assert [s.name for s in store.list()] == ["web-dashboard"]


def test_list_when_a_file_has_an_invalid_agent_name_skips_it(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    (tmp_path / "-bad.json").write_text("{}")

    assert store.list() == []
