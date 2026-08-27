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
  - [ ] FR-06: expose an OpenAPI HTTP interface for status
  - [ ] FR-07: minimal auto-refreshing web dashboard
  - [ ] FR-08: full in-browser terminal attach per agent
  - [ ] FR-09: real scrollback/rendering on attach, not replay
current_iteration: 10
current_phase: RED
last_test_added: test_poll_adapter_run_forever_calls_run_once_each_interval_via_injected_sleep
last_code_change: PollAdapter.run_forever with injectable sleep_fn
last_green_commit: PLACEHOLDER
exit_condition_met: false
