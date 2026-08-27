from agenthubctl.adapters.terminal.ttyd_adapter import TtydTerminalAdapter


def test_resolve_returns_mapped_endpoint_for_known_agent():
    adapter = TtydTerminalAdapter(endpoints={"web-dashboard": "http://127.0.0.1:7681"})

    assert adapter.resolve("web-dashboard") == "http://127.0.0.1:7681"


def test_resolve_returns_none_for_unknown_agent():
    # documents existing behavior (dict.get default) - not a new RED
    adapter = TtydTerminalAdapter(endpoints={"web-dashboard": "http://127.0.0.1:7681"})

    assert adapter.resolve("never-mapped") is None
