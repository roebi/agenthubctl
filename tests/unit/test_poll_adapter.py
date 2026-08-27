from agenthubctl.adapters.collectors.poll_adapter import PollAdapter
from agenthubctl.domain.models import StatusValue


class FakeStatusPort:
    def __init__(self):
        self.reported = []

    def report(self, agent_id, status, message=None, timestamp=None):
        self.reported.append((agent_id, status, message))

    def get(self, agent_id):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError


def test_poll_adapter_reports_status_returned_by_check_fn():
    port = FakeStatusPort()
    adapter = PollAdapter(
        agent_id="codex-worker",
        check_fn=lambda: StatusValue.WORKING,
        status_port=port,
    )

    adapter.run_once()

    assert port.reported == [("codex-worker", StatusValue.WORKING, None)]


def test_poll_adapter_run_forever_calls_run_once_each_interval_via_injected_sleep():
    port = FakeStatusPort()
    calls = []
    adapter = PollAdapter(
        agent_id="codex-worker",
        check_fn=lambda: StatusValue.IDLE,
        status_port=port,
        interval_seconds=5,
    )

    def fake_sleep(seconds):
        calls.append(seconds)
        if len(calls) >= 3:
            raise StopIteration

    try:
        adapter.run_forever(sleep_fn=fake_sleep)
    except StopIteration:
        pass

    assert calls == [5, 5, 5]
    assert len(port.reported) == 3
