#!/usr/bin/env bash
# One-command demo: builds the demo agent image, (re)starts the hub with the
# agent's terminal registered, then starts one demo agent on a shared podman
# network. Reentrant like the other podman_*.sh scripts.
#
# Usage: examples/demo-agent/run.sh   (hub image must exist: ./podman_build.sh)
#   DEMO_AGENT_NAME  agent name on the dashboard (default demo-agent)
#   DEMO_AGENT_PORT  host port for the agent's terminal (default 7681)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AGENT_IMAGE="agenthubctl-demo-agent:latest"
AGENT_NAME="${DEMO_AGENT_NAME:-demo-agent}"
AGENT_PORT="${DEMO_AGENT_PORT:-7681}"
NETWORK="agenthubctl"

cd "${REPO_DIR}"

podman build --tag "${AGENT_IMAGE}" --file examples/demo-agent/Containerfile .

# The browser opens the terminal URL from the host; 127.0.0.1 rather than
# localhost so it never depends on how the host resolves localhost.
AGENTHUBCTL_TERMINALS="${AGENT_NAME}=http://127.0.0.1:${AGENT_PORT}" ./podman_run.sh

if podman container exists "${AGENT_NAME}"; then
    podman rm -f "${AGENT_NAME}" >/dev/null
fi
podman run \
    --detach \
    --name "${AGENT_NAME}" \
    --network "${NETWORK}" \
    --publish "${AGENT_PORT}:7681" \
    --env AGENTHUBCTL_URL="http://agenthubctl:8000" \
    --env AGENTHUBCTL_AGENT="${AGENT_NAME}" \
    "${AGENT_IMAGE}" >/dev/null

echo
echo "  Demo agent '${AGENT_NAME}' started; it shows up as idle within a few seconds."
echo "  Click 'attach' on the dashboard, then in the terminal try:"
echo "    agent-status working building the thing"
echo "    agent-status blocked needs your approval"
echo "    agent-status done"
echo "  Stop: podman rm -f ${AGENT_NAME} agenthubctl"
