#!/usr/bin/env bash
# Reentrant: safe to run repeatedly - removes any prior container of the
# same name before starting a fresh one, so re-running never fails on
# "name already in use" and always leaves exactly one running instance.
#
# Usage: podman_run.sh [IMAGE_TAG]
#   AGENTHUBCTL_HOST_PORT      host port to publish (default 8000)
#   AGENTHUBCTL_STATUS_VOLUME  named volume for status files
#   AGENTHUBCTL_OPEN_BROWSER   1 (default) opens the dashboard in the default
#                              browser when a desktop session is present; 0 never
set -euo pipefail

IMAGE_NAME="agenthubctl"
IMAGE_TAG="${1:-latest}"
CONTAINER_NAME="agenthubctl"
HOST_PORT="${AGENTHUBCTL_HOST_PORT:-8000}"
STATUS_VOLUME="${AGENTHUBCTL_STATUS_VOLUME:-agenthubctl-status}"
OPEN_BROWSER="${AGENTHUBCTL_OPEN_BROWSER:-1}"
READY_TIMEOUT_SECONDS=30

DASHBOARD_URL="http://localhost:${HOST_PORT}/"
OPENAPI_URL="http://localhost:${HOST_PORT}/openapi.json"

if podman container exists "${CONTAINER_NAME}"; then
    podman rm -f "${CONTAINER_NAME}" >/dev/null
    echo "Removed previous ${CONTAINER_NAME} container"
fi

container_id="$(podman run \
    --detach \
    --name "${CONTAINER_NAME}" \
    --publish "${HOST_PORT}:8000" \
    --volume "${STATUS_VOLUME}:/data/status" \
    "${IMAGE_NAME}:${IMAGE_TAG}")"
echo "Started ${CONTAINER_NAME} (${container_id:0:12}), publishing port ${HOST_PORT}"

# Wait until the hub answers, so the links below work when they are printed.
if command -v curl >/dev/null; then
    ready=0
    for _ in $(seq 1 "${READY_TIMEOUT_SECONDS}"); do
        if curl --silent --fail --max-time 1 --output /dev/null \
            "http://127.0.0.1:${HOST_PORT}/agents"; then
            ready=1
            break
        fi
        sleep 1
    done
    if [[ "${ready}" -ne 1 ]]; then
        echo "agenthubctl did not answer within ${READY_TIMEOUT_SECONDS}s - see: podman logs ${CONTAINER_NAME}" >&2
        exit 1
    fi
fi

echo
echo "  Dashboard:    ${DASHBOARD_URL}"
echo "  OpenAPI spec: ${OPENAPI_URL}"
echo
echo "  Logs: podman logs -f ${CONTAINER_NAME}    Stop: podman rm -f ${CONTAINER_NAME}"

# Open the dashboard only on a desktop session (not in CI or over plain SSH).
open_dashboard() {
    if [[ "$(uname -s)" == "Darwin" ]]; then
        open "${DASHBOARD_URL}"
    elif [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]] && command -v xdg-open >/dev/null; then
        xdg-open "${DASHBOARD_URL}" >/dev/null 2>&1 &
    else
        return 1
    fi
}

if [[ "${OPEN_BROWSER}" == "1" ]]; then
    if open_dashboard; then
        echo "  Opened the dashboard in your default browser (AGENTHUBCTL_OPEN_BROWSER=0 to skip)"
    fi
fi
