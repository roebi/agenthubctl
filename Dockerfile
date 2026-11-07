FROM python:3.14-slim AS base

# Hub image only: serves the status API and dashboard. tmux and ttyd belong in
# each AGENT container next to agent-terminal.sh (architecture.md, FR-08/09),
# not here - the hub only hands out the agents' ttyd URLs.

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
