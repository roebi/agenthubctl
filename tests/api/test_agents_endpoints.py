from datetime import datetime, timezone

import pytest

from agenthubctl.adapters.store.file_store import FileStatusStore
from agenthubctl.adapters.terminal.ttyd_adapter import TtydTerminalAdapter
from agenthubctl.api import app as app_module
from agenthubctl.domain.models import StatusValue


def make_client(store, endpoints=None):
    terminal = TtydTerminalAdapter(endpoints=endpoints or {})
    return app_module.create_app(status_port=store, terminal_port=terminal).test_client()


@pytest.fixture
def client(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    store.report("web-dashboard", StatusValue.BLOCKED, timestamp=datetime.now(timezone.utc))
    return make_client(store)


def test_get_agents_returns_all_statuses(client):
    response = client.get("/agents")

    assert response.status_code == 200
    names = {agent["name"] for agent in response.json()}
    assert names == {"web-dashboard"}


def test_get_agent_by_name_returns_that_agent(client):
    response = client.get("/agents/web-dashboard")

    assert response.status_code == 200
    assert response.json()["name"] == "web-dashboard"
    assert response.json()["status"] == "blocked"


def test_get_agent_returns_404_for_unknown_agent(client):
    response = client.get("/agents/never-reported")

    assert response.status_code == 404


def test_get_agent_with_invalid_name_returns_400(client):
    response = client.get("/agents/-starts-with-dash")

    assert response.status_code == 400


def test_post_agent_status_records_the_status(client):
    response = client.post("/agents/data-pipeline/status", json={"status": "working"})

    assert response.status_code == 204
    follow_up = client.get("/agents/data-pipeline")
    assert follow_up.json()["status"] == "working"


def test_post_agent_status_with_invalid_name_returns_400_and_stores_nothing(client):
    response = client.post("/agents/.hidden/status", json={"status": "working"})

    assert response.status_code == 400
    assert {a["name"] for a in client.get("/agents").json()} == {"web-dashboard"}


def test_post_hook_notification_event_marks_agent_blocked(client):
    response = client.post(
        "/agents/data-pipeline/hook",
        json={"hook_event_name": "Notification", "session_id": "abc", "message": "x"},
    )

    assert response.status_code == 204
    assert client.get("/agents/data-pipeline").json()["status"] == "blocked"


def test_post_hook_stop_event_marks_agent_done(client):
    response = client.post("/agents/web-dashboard/hook", json={"hook_event_name": "Stop"})

    assert response.status_code == 204
    assert client.get("/agents/web-dashboard").json()["status"] == "done"


def test_post_hook_unknown_event_is_accepted_and_changes_nothing(client):
    response = client.post("/agents/web-dashboard/hook", json={"hook_event_name": "PreToolUse"})

    assert response.status_code == 204
    assert client.get("/agents/web-dashboard").json()["status"] == "blocked"


def test_two_apps_when_created_with_different_stores_stay_independent(tmp_path):
    # architecture.md: create_app is a factory with no global state - a second
    # app must not rewire the first one
    first_store = FileStatusStore(base_dir=tmp_path / "first")
    first_store.report("only-in-first", StatusValue.WORKING)
    second_store = FileStatusStore(base_dir=tmp_path / "second")
    second_store.report("only-in-second", StatusValue.IDLE)

    first = make_client(first_store)
    make_client(second_store)

    assert {a["name"] for a in first.get("/agents").json()} == {"only-in-first"}


def test_get_agent_terminal_returns_the_resolved_endpoint(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    store.report("web-dashboard", StatusValue.BLOCKED)
    client = make_client(store, endpoints={"web-dashboard": "http://127.0.0.1:7681"})

    response = client.get("/agents/web-dashboard/terminal")

    assert response.status_code == 200
    assert response.json()["url"] == "http://127.0.0.1:7681"


def test_get_agent_terminal_returns_404_for_unresolvable_agent(tmp_path):
    client = make_client(FileStatusStore(base_dir=tmp_path))

    response = client.get("/agents/never-mapped/terminal")

    assert response.status_code == 404


def test_dashboard_route_serves_html(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "agenthubctl" in response.text


def test_dashboard_never_renders_agent_data_as_html(client):
    # agent names and messages come from unauthenticated POSTs; rendering them
    # through innerHTML is stored XSS - the dashboard must use textContent
    html = client.get("/").text

    assert "innerHTML" not in html
    assert "textContent" in html


def test_dashboard_url_encodes_agent_name_in_terminal_request(client):
    html = client.get("/").text

    assert "encodeURIComponent(name)" in html
