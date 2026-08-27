#!/usr/bin/env bash
set -euo pipefail

exec agenthubctl \
    --host "${AGENTHUBCTL_HOST:-0.0.0.0}" \
    --port "${AGENTHUBCTL_PORT:-8000}" \
    --status-dir "${AGENTHUBCTL_STATUS_DIR:-/data/status}"
