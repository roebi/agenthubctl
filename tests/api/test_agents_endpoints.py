from datetime import datetime, timezone

import pytest

from agenthubctl.adapters.store.file_store import FileStatusStore
from agenthubctl.api import app as app_module
from agenthubctl.domain.models import StatusValue


@pytest.fixture
def client(tmp_path):
    store = FileStatusStore(base_dir=tmp_path)
    store.report("web-dashboard", StatusValue.BLOCKED, timestamp=datetime.now(timezone.utc))
    app = app_module.create_app(status_port=store, terminal_port=None)
    return app.test_client()


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


def test_post_agent_status_records_the_status(client):
    response = client.post("/agents/data-pipeline/status", json={"status": "working"})

    assert response.status_code == 204
    follow_up = client.get("/agents/data-pipeline")
    assert follow_up.json()["status"] == "working"
