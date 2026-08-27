class TtydTerminalAdapter:
    def __init__(self, endpoints: dict[str, str]) -> None:
        self._endpoints = endpoints

    def resolve(self, agent_id: str) -> str | None:
        return self._endpoints.get(agent_id)
