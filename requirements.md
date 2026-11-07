# Requirements

## Purpose

Control a hub of n coding agent loops (Claude Code, Codex, etc.),
each running in its own Podman container, via status reporting and
in-browser terminal attach.

## Functional Requirements

FR-01: Report an agent's status (working, blocked, idle, or done),
       with an optional message and a timestamp, via a status-reporting
       mechanism specific to that agent's type.
FR-02: Return the status of all registered agents.
FR-03: Return the status of a single named agent.
FR-04: Persist each agent's most recent status such that it survives
       a process restart.
FR-05: Support agent-type-specific status reporting. v1: event-driven
       only - Claude Code hook payloads (POST /agents/{name}/hook)
       plus direct status reports (POST /agents/{name}/status) that
       any agent type able to make an HTTP call can use. The
       interval-based fallback for agent types that cannot report on
       their own is descoped for v1 (see Out of Scope).
FR-06: Expose an HTTP interface, described by an OpenAPI specification,
       for listing and retrieving agent statuses, consumable by
       external controller software.
FR-07: Provide a minimal web dashboard that displays all agent
       statuses and refreshes automatically.
FR-08: Allow a user to open a full interactive terminal session into
       any named agent's running process directly from the dashboard,
       to enter input.
FR-09: Preserve full terminal scrollback and correct visual rendering
       when attaching to an agent's terminal - not a replay or
       re-entry of prior state.

## Non-Functional Requirements

NFR-01: Portability - runs on Linux under rootless Podman; no
        macOS-only dependency.
NFR-02: Security - CI must run static analysis (bash and Python) and
        container vulnerability scanning, plus dynamic testing on
        live containers, before release.
NFR-03: Testability - implemented test-first; the status persistence
        and HTTP layers must have automated tests before a phase
        counts as done.
NFR-04: Reliability - a status write must never be readable in a
        partially-written state.
NFR-05: Maintainability - the status persistence mechanism must be
        replaceable without changing the HTTP interface or the
        status-reporting mechanisms.

## Planned for the Next Version

- Control agents through the OpenAPI interface, not only observe them:
  e.g. send input to an agent's terminal session (answer a blocked agent,
  send a prompt), so the use cases "for agents" and "for automation" can
  act, not just read. Decided 2026-11-07; to be specified in a
  gather-requirements-en round for that version.

## Out of Scope

- Spawning, stopping, or otherwise managing the lifecycle of agent
  containers (status and attach only, not orchestration of containers)
- Task backlog, ticket assignment, or work dispatch to agents
- Multi-user authentication or access control on the dashboard
- Interval-based (polling) status collection for agent types that
  cannot report on their own - descoped for v1 on 2026-11-07 because
  no poll-based agent type or blocked-state heuristic was chosen.
  PollAdapter was removed from the codebase; it can be recovered from
  git history for a later version.

## Rejected Alternative

- Adopting herdr.dev directly: Podman already provides the session
  persistence herdr's server offers for this architecture; only the
  status-awareness gap needed a custom build, hence agenthubctl instead
  of adopting an external runtime.
