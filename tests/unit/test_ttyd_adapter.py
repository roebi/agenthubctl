from agenthubctl.adapters.terminal.ttyd_adapter import TtydTerminalAdapter


def test_resolve_returns_mapped_endpoint_for_known_agent():
    adapter = TtydTerminalAdapter(endpoints={"web-dashboard": "http://127.0.0.1:7681"})

    assert adapter.resolve("web-dashboard") == "http://127.0.0.1:7681"
