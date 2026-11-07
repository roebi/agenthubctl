# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-07

### Added

- Status hub for parallel coding agents: each agent reports `working`,
  `blocked`, `idle` or `done` with an optional message and timestamp.
- OpenAPI HTTP interface: `GET /agents`, `GET /agents/{name}`,
  `POST /agents/{name}/status`, `POST /agents/{name}/hook`,
  `GET /agents/{name}/terminal`, specification at `GET /openapi.json`.
- Claude Code hook support: SessionStart, UserPromptSubmit, PreToolUse,
  Notification (with its message) and Stop are mapped to statuses; other
  events are ignored.
- Web dashboard listing all agents, refreshing every 3 seconds, with the
  last update shown as `YYYYMMDD HHMI` in the browser's local time (the API
  keeps ISO 8601) and an attach link per agent that opens its live terminal
  in a new tab.
- `agent-terminal.sh` for agent containers: runs the agent in tmux with a
  50000-line scrollback and serves the same session through ttyd, so
  re-attaching rejoins the session instead of starting a new shell.
- File-based status store, one JSON file per agent, written atomically so a
  status is never read half-written, and kept across restarts.
- `--terminal NAME=URL` option and `AGENTHUBCTL_TERMINALS` environment
  variable to register agent terminals (http and https URLs only).
- Container image for the hub (installs from `uv.lock`, runs as non-root),
  with `podman_build.sh` and `podman_run.sh`; `podman_run.sh` waits until
  the hub answers, prints the dashboard and OpenAPI links and opens the
  dashboard in the browser on a desktop session.
- Examples: Claude Code hook forwarding (`examples/claude-code-hooks/`) and
  a demo agent container (`examples/demo-agent/`).
- MIT license.

### Security

- Agent names are validated (no path traversal into the status directory)
  and agent data is rendered as text only in the dashboard (no stored XSS).
- No authentication: run the hub and the agents' ttyd ports on a trusted
  machine or network only.

[unreleased]: https://github.com/roebi/agenthubctl/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/roebi/agenthubctl/releases/tag/v0.1.0
