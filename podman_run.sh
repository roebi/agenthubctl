#!/usr/bin/env bash
# Reentrant: safe to run repeatedly - removes any prior container of the
# same name before starting a fresh one, so re-running never fails on
# "name already in use" and always leaves exactly one running instance.
set -euo pipefail

IMAGE_NAME="agenthubctl"
IMAGE_TAG="${1:-latest}"
CONTAINER_NAME="agenthubctl"
HOST_PORT="${AGENTHUBCTL_HOST_PORT:-8000}"
STATUS_VOLUME="${AGENTHUBCTL_STATUS_VOLUME:-agenthubctl-status}"

if podman container exists "${CONTAINER_NAME}"; then
    podman rm -f "${CONTAINER_NAME}"
fi

podman run \
    --detach \
    --name "${CONTAINER_NAME}" \
    --publish "${HOST_PORT}:8000" \
    --volume "${STATUS_VOLUME}:/data/status" \
    "${IMAGE_NAME}:${IMAGE_TAG}"

echo "Running ${CONTAINER_NAME}, publishing port ${HOST_PORT}"
