FROM python:3.14-slim AS build

# Hub image only: serves the status API and dashboard. tmux and ttyd belong in
# each AGENT container next to agent-terminal.sh (architecture.md, FR-08/09),
# not here - the hub only hands out the agents' ttyd URLs.

# Installs exactly the versions pinned in uv.lock (--frozen fails if the lock
# is out of date) into /app/.venv; the runtime stage copies only that venv.
RUN pip install --no-cache-dir uv==0.13.7
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
# README.md and LICENSE are referenced by pyproject.toml (readme, license-files)
COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable

FROM python:3.14-slim

ARG APP_UID=10001
# - apt-get upgrade: Debian security fixes newer than the base image
# - pip is removed: the hub runs from /app/.venv and never needs it, and pip's
#   bundled copies of urllib3, msgpack and setuptools are flagged by Trivy
# - /data/status is created owned by the app user so a fresh named volume
#   mounted there (podman_run.sh) inherits a writable owner
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip uninstall -y pip \
    && useradd --system --uid "${APP_UID}" --no-create-home agenthubctl \
    && mkdir -p /data/status \
    && chown agenthubctl /data/status

COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:${PATH}"
COPY --chmod=755 entrypoint.sh /entrypoint.sh

USER agenthubctl
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
