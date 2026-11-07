import pytest

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


def test_hook_adapter_on_notification_event_reports_blocked():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="web-dashboard", status_port=port)

    adapter.handle_hook_event({"hook_event_name": "Notification"})

    assert port.reported == [("web-dashboard", StatusValue.BLOCKED, None)]


def test_hook_adapter_on_stop_event_reports_done():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="data-pipeline", status_port=port)

    adapter.handle_hook_event({"hook_event_name": "Stop"})

    assert port.reported == [("data-pipeline", StatusValue.DONE, None)]


def test_hook_adapter_on_notification_event_keeps_its_message():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="web-dashboard", status_port=port)

    adapter.handle_hook_event(
        {"hook_event_name": "Notification", "message": "Claude needs your permission"}
    )

    assert port.reported == [
        ("web-dashboard", StatusValue.BLOCKED, "Claude needs your permission")
    ]


def test_hook_adapter_on_notification_with_non_string_message_drops_it():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="web-dashboard", status_port=port)

    adapter.handle_hook_event({"hook_event_name": "Notification", "message": 42})

    assert port.reported == [("web-dashboard", StatusValue.BLOCKED, None)]


@pytest.mark.parametrize("event", ["UserPromptSubmit", "PreToolUse"])
def test_hook_adapter_on_activity_event_reports_working(event):
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="data-pipeline", status_port=port)

    adapter.handle_hook_event({"hook_event_name": event})

    assert port.reported == [("data-pipeline", StatusValue.WORKING, None)]


def test_hook_adapter_on_session_start_event_reports_idle():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="data-pipeline", status_port=port)

    adapter.handle_hook_event({"hook_event_name": "SessionStart"})

    assert port.reported == [("data-pipeline", StatusValue.IDLE, None)]


def test_hook_adapter_on_unknown_event_reports_nothing():
    port = FakeStatusPort()
    adapter = HookAdapter(agent_id="data-pipeline", status_port=port)

    adapter.handle_hook_event({"hook_event_name": "PostCompact"})

    assert port.reported == []
