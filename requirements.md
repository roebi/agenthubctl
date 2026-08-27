# Requirements

## Functional Requirements

FR-01: Report an agent's status (working, blocked, idle, or done),
       with an optional message and a timestamp, via a status-reporting
       mechanism specific to that agent's type.
FR-02: Return the status of all registered agents.
FR-03: Return the status of a single named agent.
FR-04: Persist each agent's most recent status such that it survives
       a process restart.
FR-05: Support at least two distinct agent types via their own
       status-reporting mechanism - one that reports status on its own
       (event-driven) and one that must be checked periodically
       (interval-based fallback), selected per agent type.
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

## Out of Scope

- Spawning, stopping, or otherwise managing the lifecycle of agent
  containers (status and attach only, not orchestration of containers)
- Task backlog, ticket assignment, or work dispatch to agents
- Multi-user authentication or access control on the dashboard
