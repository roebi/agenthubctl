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
