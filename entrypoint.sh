#!/usr/bin/env bash
set -euo pipefail

# An empty host listens on every address, IPv4 and IPv6: "localhost" on the
# podman host often resolves to ::1 first, and a 0.0.0.0-only bind then fails
# for http://localhost:PORT while http://127.0.0.1:PORT works.
exec agenthubctl \
    --host "${AGENTHUBCTL_HOST:-}" \
    --port "${AGENTHUBCTL_PORT:-8000}" \
    --status-dir "${AGENTHUBCTL_STATUS_DIR:-/data/status}"
