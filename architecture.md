# Architecture

## Summary

A small hexagonal Python service. A status port and a terminal-access
port sit at the center; one collector adapter (push via
hooks) and one store adapter feed the status port; a Connexion
v3 API and a static HTML dashboard sit on top; a thin Typer CLI wires
concrete adapters together and starts the service. One module per
responsibility, nothing added beyond what FR-01..FR-09 require.

## Module Structure

```
agenthubctl/
  src/agenthubctl/
    __init__.py
    cli.py                        # Typer entry point, thin wrapper
    domain/
      __init__.py
      models.py                   # AgentStatus, StatusValue
      ports.py                    # AgentStatusPort, AgentTerminalAccessPort
    adapters/
      collectors/
        hook_adapter.py           # HookAdapter (push)
      store/
        file_store.py             # FileStatusStore (AgentStatusPort impl)
      terminal/
        ttyd_adapter.py           # TtydTerminalAdapter (AgentTerminalAccessPort impl)
    api/
      openapi.json                # written before app.py, per API-first
      app.py                      # Connexion v3 app factory
    dashboard/
      static/index.html           # FR-07 dashboard
  tests/
    unit/
      test_file_store.py
      test_hook_adapter.py
      test_ttyd_adapter.py
    api/
      test_agents_endpoints.py
    integration/
      test_agent_terminal.py      # FR-09, real tmux, ttyd stubbed
  pyproject.toml
  requirements.md
  architecture.md
  Handover-State.md
  agent-terminal.sh               # runs in each AGENT container: tmux + ttyd (FR-08, FR-09)
  .github/workflows/ci.yml
```

## Components

### domain.models.AgentStatus
- Responsibility: represent one agent's status - name, status value,
  timestamp, optional message.
- Public interface: `AgentStatus` (pydantic model), `StatusValue`
  enum (working, blocked, idle, done).
- Dependencies: none - pure data.

### domain.ports.AgentStatusPort
- Responsibility: contract for reporting and reading agent status
  (FR-01..FR-04).
- Public interface: `report(agent_id, status, message=None) -> None`,
  `list() -> list[AgentStatus]`, `get(agent_id) -> AgentStatus | None`.
- Dependencies: domain.models only.

### domain.ports.AgentTerminalAccessPort
- Responsibility: contract for resolving an agent's terminal
  endpoint (FR-08, FR-09).
- Public interface: `resolve(agent_id) -> str | None` (the ttyd URL).
- Dependencies: domain.models only.

### adapters.store.file_store.FileStatusStore
- Responsibility: implements AgentStatusPort as one JSON file per
  agent, atomic write via tmp-file plus rename (FR-04, NFR-04).
- Public interface: implements AgentStatusPort.
- Dependencies: domain.ports; an injected base `Path`.

### adapters.collectors.hook_adapter.HookAdapter
- Responsibility: receives a Claude Code hook payload (Notification,
  Stop) and reports status through the port (FR-01, FR-05
  event-driven case).
- Public interface: `handle_hook_event(payload: dict) -> None`.
- Dependencies: an injected AgentStatusPort.

### adapters.terminal.ttyd_adapter.TtydTerminalAdapter
- Responsibility: implements AgentTerminalAccessPort by resolving an
  agent name to its container's ttyd endpoint (FR-08, FR-09).
- Public interface: implements AgentTerminalAccessPort.
- Dependencies: domain.ports; an injected agent-id-to-endpoint
  mapping.

### api.app
- Responsibility: Connexion v3 app wiring the OpenAPI spec to the
  ports - GET /agents, GET /agents/{name}, POST /agents/{name}/status
  (FR-02, FR-03, FR-06), POST /agents/{name}/hook passing a raw Claude
  Code hook payload through HookAdapter (FR-05 event-driven case), and
  GET /agents/{name}/terminal returning the ttyd endpoint (FR-08).
  Agent names are validated against one pattern
  (domain.models.AGENT_NAME_PATTERN, mirrored in openapi.json).
- Public interface: `create_app(status_port, terminal_port) -> App`
  (factory, no globals - handlers are closures over that app's ports,
  bound to operationIds through a Connexion `Resolver`).
- Dependencies: domain.ports; adapters.collectors.HookAdapter;
  api/openapi.json.

### dashboard (static HTML/JS)
- Responsibility: polls GET /agents, renders status per agent, links
  each agent's attach action to its ttyd endpoint (FR-07, FR-08).
- Public interface: static assets served by api.app.
- Dependencies: api.app's endpoints only - no server-side logic of
  its own.

### cli.py
- Responsibility: thin entry point; wires a concrete FileStatusStore
  and TtydTerminalAdapter into api.app.create_app and runs it.
- Public interface: `agenthubctl` (Typer collapses a single
  `@app.command()` to the app's default command directly - there is
  no separate `serve` subcommand word to type; corrected from this
  document's original claim after a test caught the discrepancy).
  Terminal endpoints are configured with repeatable
  `--terminal NAME=URL` (or `AGENTHUBCTL_TERMINALS`), http(s) only.
- Dependencies: api.app.create_app; concrete adapters - no logic of
  its own.

## Data Flow

Agent containers POST status (POST /agents/{name}/status) or raw hook
payloads (POST /agents/{name}/hook -> HookAdapter); collector adapters
call
`AgentStatusPort.report()` -> FileStatusStore writes the status as an
atomic JSON file -> api.app's GET endpoints read it back through
`AgentStatusPort.list()` / `get()` -> the dashboard polls those
endpoints and renders them -> on an attach click, the dashboard calls
GET /agents/{name}/terminal -> TtydTerminalAdapter resolves the
container's ttyd URL -> the browser opens that URL directly, giving a
real PTY session (xterm.js served by ttyd itself, not proxied through
this app).

## Technology Choices

| Decision | Choice | Rationale |
|---|---|---|
| Language/runtime | Python 3.14 only, src layout, no version matrix | newest stable Python pinned per explicit instruction (3.15 is pre-release) |
| CLI | Typer | skill default; thin wrapper, free --install-completion |
| HTTP API | Connexion v3, openapi.json written first | his API-first default; satisfies FR-06 |
| Testing | pytest + pytest-cov | skill default |
| Dependency management | uv | skill default; also used to install/pin Python 3.14 itself |
| Linting | ruff | skill default |
| CI | GitHub Actions, single Python 3.14 job, plus security gates | skill default (minus matrix, per pinned-version instruction) + NFR-02 (ShellCheck, semgrep/bandit, Trivy/Grype, DAST) |
| Status store | flat directory, one JSON file per agent, tmp+rename | FR-04, NFR-04; KISS - no DB needed at this scale |
| Terminal transport | tmux + ttyd inside each agent container | FR-08, FR-09; avoids building a custom PTY-over-websocket bridge |
| Containerization | rootless Podman, reentrant build/run scripts | NFR-01; reuses the existing claude-code-podman scaffold |

## Testability Constraints

- File I/O (FileStatusStore): base `Path` is injected in the
  constructor; tests use a tmp directory, no real status dir needed.
- HookAdapter: takes AgentStatusPort as a constructor dependency
  (protocol); tests use an in-memory fake port.
- TtydTerminalAdapter: the agent-id-to-endpoint mapping is injected;
  tests need no real container or ttyd process.
- api.app: `create_app(status_port, terminal_port)` takes both ports
  as parameters; tests wire in-memory fakes and use Connexion's test
  client - no real store or containers required.
- No global state anywhere - every adapter and the app factory take
  their dependencies as constructor or factory arguments.

## Open Questions

- Exact Claude Code hook payload shape for Notification/Stop events -
  needs confirming against a real hook invocation before
  HookAdapter's parsing logic is finalized in the implement phase.
- Which agent type is the second (poll-based) one - Codex or
  something else - and what its blocked-state heuristic looks like.
  Resolved for v1 by descoping: polling is out of scope (see
  requirements.md); PollAdapter was removed on 2026-11-07 and can be
  recovered from git history (commit before its removal) if needed.
- Dashboard refresh mechanism - FR-07 allows polling or SSE; plan to
  start with polling as the simpler option unless a reason emerges
  during implementation.
- ttyd endpoint access control - requirements.md places
  authentication out of scope for v1; worth flagging again before any
  non-local deployment.
