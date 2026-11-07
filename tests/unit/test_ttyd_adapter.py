from agenthubctl.adapters.terminal.ttyd_adapter import TtydTerminalAdapter


def test_resolve_with_known_agent_returns_its_endpoint():
    adapter = TtydTerminalAdapter(endpoints={"web-dashboard": "http://127.0.0.1:7681"})

    assert adapter.resolve("web-dashboard") == "http://127.0.0.1:7681"


def test_resolve_with_unknown_agent_returns_none():
    # documents existing behavior (dict.get default) - not a new RED
    adapter = TtydTerminalAdapter(endpoints={"web-dashboard": "http://127.0.0.1:7681"})

    assert adapter.resolve("never-mapped") is None
