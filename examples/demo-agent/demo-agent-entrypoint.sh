#!/usr/bin/env bash
# Reports "idle" once the hub answers, then hands over to agent-terminal.sh,
# which starts bash in tmux and serves it through ttyd on port 7681.
set -euo pipefail

: "${AGENTHUBCTL_URL:?set AGENTHUBCTL_URL}"
: "${AGENTHUBCTL_AGENT:?set AGENTHUBCTL_AGENT}"
HUB_WAIT_SECONDS=30

for _ in $(seq 1 "${HUB_WAIT_SECONDS}"); do
    if agent-status idle "demo agent started - attach and try: agent-status working building" >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

exec agent-terminal.sh "${AGENTHUBCTL_AGENT}" 7681 -- bash -l
