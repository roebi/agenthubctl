from agenthubctl.adapters.collectors.hook_adapter import HookAdapter
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


def test_hook_adapter_reports_blocked_on_notification_event():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="web-dashboard", status_port=port)

    adapter.handle_hook_event({"hook_event_name": "Notification"})

    assert port.reported == [("web-dashboard", StatusValue.BLOCKED, None)]


def test_hook_adapter_reports_done_on_stop_event():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="data-pipeline", status_port=port)

    adapter.handle_hook_event({"hook_event_name": "Stop"})

    assert port.reported == [("data-pipeline", StatusValue.DONE, None)]
