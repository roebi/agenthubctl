#!/usr/bin/env bash
# Runs inside each AGENT container as a Claude Code hook command (FR-05).
#
# Claude Code writes the hook payload as JSON to the hook's stdin; this
# forwards it unchanged to the hub, which maps hook_event_name to a status
# (see src/agenthubctl/adapters/collectors/hook_adapter.py).
#
#   AGENTHUBCTL_URL    hub base URL, e.g. http://agenthubctl:8000
#   AGENTHUBCTL_AGENT  this agent's name, e.g. web-dashboard
#
# Never blocks or fails the agent: short timeout, errors ignored, exit 0.
set -uo pipefail

: "${AGENTHUBCTL_URL:?set AGENTHUBCTL_URL}"
: "${AGENTHUBCTL_AGENT:?set AGENTHUBCTL_AGENT}"

curl --silent --show-error --max-time 2 \
    --request POST \
    --header "Content-Type: application/json" \
    --data-binary @- \
    "${AGENTHUBCTL_URL}/agents/${AGENTHUBCTL_AGENT}/hook" >/dev/null || true
exit 0
