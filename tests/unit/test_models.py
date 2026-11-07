from datetime import UTC, datetime

from agenthubctl.domain.models import AgentStatus, StatusValue


def test_agent_status_when_given_all_fields_holds_them():
    ts = datetime.now(UTC)

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


def test_agent_status_without_message_defaults_it_to_none():
    status = AgentStatus(
        name="data-pipeline",
        status=StatusValue.WORKING,
        timestamp=datetime.now(UTC),
    )

    assert status.message is None


def test_status_value_when_enumerated_has_exactly_four_states():
    assert {v.value for v in StatusValue} == {"working", "blocked", "idle", "done"}
