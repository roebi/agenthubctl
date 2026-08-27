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
