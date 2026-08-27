#!/usr/bin/env bash
# Reentrant: safe to run repeatedly - always produces a fresh, correctly
# tagged image, overwriting any previous build under the same tag.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="agenthubctl"
IMAGE_TAG="${1:-latest}"

cd "${SCRIPT_DIR}"

podman build \
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
    --file Dockerfile \
    .

echo "Built ${IMAGE_NAME}:${IMAGE_TAG}"
