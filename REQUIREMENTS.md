# Requirements - agenthubctl

Status: approved plan.
Architecture: hexagonal (ports + adapters).

Purpose: control a hub of n coding agent loops (Claude Code, Codex, etc.),
each running in its own Podman container, via status reporting and
in-browser terminal attach.

---

## R-STORE - status persistence

- R-STORE-001: one file per agent, `status/<agent-name>.json`
- R-STORE-002: atomic write - write to tmp file, then rename
- R-STORE-003: schema - name, status (working|blocked|idle|done),
  timestamp, optional message
- R-STORE-004: store is a swappable repository adapter behind the
  status port (directory now, DB later without touching callers)

## R-COLLECT - status collectors

- R-COLLECT-001: AgentStatusPort - report(agent_id, status, message?),
  list() -> [AgentStatus]
- R-COLLECT-002: HookAdapter - push-based, for agents with a hook
  system (Claude Code Notification/Stop hooks)
- R-COLLECT-003: PollAdapter - fallback for a second agent type
  without hooks (Codex, tbd)
- R-COLLECT-004: hook-vs-poll decided per agent type, never globally

## R-API - OpenAPI layer

- R-API-001: Python, Connexion v3, openapi.json defined before any
  route code
- R-API-002: GET /agents - list all agent statuses
- R-API-003: GET /agents/{name} - single agent status
- R-API-004: POST /agents/{name}/status - single write path; both
  collector adapters call this instead of writing files directly

## R-UI - dashboard

- R-UI-001: minimal HTML dashboard, consumes the OpenAPI GET endpoints
- R-UI-002: polling or SSE refresh
- R-UI-003: per-agent attach action, opens the agent's ttyd endpoint

## R-ATTACH - terminal access (separate from status)

- R-ATTACH-001: AgentTerminalAccessPort, decoupled from AgentStatusPort
- R-ATTACH-002: full in-browser terminal - real PTY, not proxied
  keystrokes (Claude Code's TUI needs real terminal control sequences
  and real scrollback)
- R-ATTACH-003: agent runs inside tmux in-container; ttyd bound to
  `tmux attach` inside the container
- R-ATTACH-004: port implementation resolves agent name -> that
  container's ttyd endpoint

## R-INFRA - delivery defaults

- R-INFRA-001: rootless Podman; reentrant podman_build.sh and
  podman_run.sh, Dockerfile, entrypoint.sh
- R-INFRA-002: git commit identity - github profile
  (roebi@users.noreply.github.com)
- R-INFRA-003: CI security gates - ShellCheck (bash), semgrep/bandit
  (Python SAST), npm audit (if any Node), Trivy/Grype (Docker),
  DAST on live containers

---

## Rejected alternative

- Adopting herdr.dev directly: Podman already provides the session
  persistence herdr's server offers for this architecture; only the
  status-awareness gap needed a custom build, hence agenthubctl instead
  of adopting an external runtime.
