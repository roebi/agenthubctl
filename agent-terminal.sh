#!/usr/bin/env bash
# Runs inside each AGENT container (not the agenthubctl hub) - FR-08, FR-09.
#
# Starts the agent command in a detached tmux session with a large scrollback
# buffer, then serves that same session through ttyd. ttyd runs
# "tmux attach-session" for every browser client, so an attach joins the live
# session: tmux redraws the current screen and keeps the full history, instead
# of starting a new shell or replaying output. Re-running the script never
# restarts the agent - an existing session is reused.
#
# Usage: agent-terminal.sh SESSION PORT -- COMMAND [ARGS...]
#   AGENT_TERMINAL_HISTORY_LIMIT  scrollback lines kept by tmux (default 50000)
#   TTYD_BIN                      ttyd executable (default: ttyd)
#
# Register the printed URL with the hub: agenthubctl --terminal SESSION=http://<host>:PORT
set -euo pipefail

usage() {
    echo "usage: $0 SESSION PORT -- COMMAND [ARGS...]" >&2
    exit 2
}

[[ $# -ge 4 && "$3" == "--" ]] || usage
SESSION="$1"
PORT="$2"
shift 3

HISTORY_LIMIT="${AGENT_TERMINAL_HISTORY_LIMIT:-50000}"
TTYD_BIN="${TTYD_BIN:-ttyd}"

if ! tmux has-session -t "=${SESSION}" 2>/dev/null; then
    # history-limit only applies to windows created after it is set, so it is
    # set on the server in the same invocation, before new-session creates the
    # agent's window
    tmux start-server \; \
        set-option -g history-limit "${HISTORY_LIMIT}" \; \
        new-session -d -s "${SESSION}" "$@"
fi

# --writable: ttyd >= 1.7 is read-only by default; FR-08 requires input
exec "${TTYD_BIN}" --port "${PORT}" --writable tmux attach-session -t "=${SESSION}"
