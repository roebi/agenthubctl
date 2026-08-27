skill: apply-tdd-loop-en
entry_point: A
language: Python 3.14
test_framework: pytest
requirements:
  - [x] FR-01: report an agent's status (working|blocked|idle|done) with optional message and timestamp
  - [x] FR-02: return the status of all registered agents
  - [x] FR-03: return the status of a single named agent
  - [x] FR-04: persist each agent's most recent status across process restarts
  - [x] FR-05: support >=2 agent types via event-driven and interval-based collectors
  - [x] FR-06: expose an OpenAPI HTTP interface for status
  - [ ] FR-07: minimal auto-refreshing web dashboard
  - [x] FR-08: full in-browser terminal attach per agent (backend endpoint; static dashboard link still open)
  - [ ] FR-09: real scrollback/rendering on attach, not replay (delivered by ttyd itself, not this app's code - verify in architecture note)
current_iteration: 17
current_phase: RED
last_test_added: test_get_agent_terminal_returns_404_for_unresolvable_agent
last_code_change: api/app.py - full CRUD-ish surface over AgentStatusPort and AgentTerminalAccessPort, ProblemException for 404s
last_green_commit: PLACEHOLDER
exit_condition_met: false
