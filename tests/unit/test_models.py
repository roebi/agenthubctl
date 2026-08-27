from datetime import datetime, timezone

from agenthubctl.domain.models import AgentStatus, StatusValue


def test_agent_status_holds_name_status_timestamp_and_optional_message():
    ts = datetime.now(timezone.utc)

    status = AgentStatus(
        name="web-dashboard",
        status=StatusValue.BLOCKED,
        timestamp=ts,
        message="waiting for permission to deploy",
    )

    assert status.name == "web-dashboard"
    assert status.status == StatusValue.BLOCKED
    assert status.timestamp == ts
    assert status.message == "waiting for permission to deploy"


def test_agent_status_message_defaults_to_none():
    status = AgentStatus(
        name="data-pipeline",
        status=StatusValue.WORKING,
        timestamp=datetime.now(timezone.utc),
    )

    assert status.message is None


def test_status_value_has_exactly_the_four_defined_states():
    assert {v.value for v in StatusValue} == {"working", "blocked", "idle", "done"}
