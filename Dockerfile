FROM python:3.14-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
        tmux \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ttyd - no Debian package; install the pinned prebuilt binary (FR-08, FR-09)
ARG TTYD_VERSION=1.7.7
RUN curl -fsSL -o /usr/local/bin/ttyd \
        "https://github.com/tsl0922/ttyd/releases/download/${TTYD_VERSION}/ttyd.x86_64" \
    && chmod +x /usr/local/bin/ttyd

WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
