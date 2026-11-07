# Code Review Checklist

Skill: code-review-en
Round: 4 (minor fixes 9-22 applied; round 3 verified fix 3 with tmux)
Reviewed commit: 7cc1414 (main), plus the round-4 fixes below
Date: 2026-11-07
Environment: Python 3.14.10, uv, ruff 0.16.5, tmux 3.3a. No podman in this
container. Round 2 (commit 57ecb4c + fix 23) found the same state minus the
tmux run. Round 1 (static only, commit
62fd50f) is in git history; its fixes are summarized under Fix History.

## Requirements Coverage

| FR | Covered by test | Test passes | Notes |
|---|---|---|---|
| FR-01 | yes | yes | test_report_then_get_returns_the_reported_status, test_post_agent_status_records_the_status, test_hook_adapter_* |
| FR-02 | yes | yes | test_get_agents_returns_all_statuses, test_list_returns_all_reported_statuses |
| FR-03 | yes | yes | test_get_agent_by_name_returns_that_agent, test_get_agent_returns_404_for_unknown_agent, test_get_agent_with_invalid_name_returns_400 |
| FR-04 | yes | yes | atomic write, concurrent tmp file, test_get_after_restart_returns_the_status_reported_before (fix 9) |
| FR-05 | yes | yes | test_hook_adapter_* (SessionStart, UserPromptSubmit, PreToolUse, Notification incl. message, Stop, unknown), test_post_hook_*; example verified end to end against a running hub (fix 22); polling descoped for v1 |
| FR-06 | yes | yes | all endpoints exercised through the spec-routed app; test_openapi_spec_when_requested_is_served (fix 9) |
| FR-07 | yes | yes | dashboard served, XSS-safe rendering, test_dashboard_when_loaded_refreshes_on_an_interval (fix 9) |
| FR-08 | yes | yes | test_build_app_when_terminal_configured_serves_its_url (real CLI wiring), terminal 200/404 API tests, --terminal parsing incl. javascript: rejection; AGENTHUBCTL_TERMINALS env var splitting verified by manual probe |
| FR-09 | yes | yes | all 4 tests in tests/integration/test_agent_terminal.py run against real tmux 3.3a (after fix 24); scrollback test verified to fail with AGENT_TERMINAL_HISTORY_LIMIT=2000 |

## Architecture Compliance

- [x] Module structure matches architecture.md (extra test_cli.py, test_models.py justified)
- [x] No module has more than one responsibility
- [x] Side effects are isolated per design - create_app binds ports in closures, verified by test_two_apps_when_created_with_different_stores_stay_independent
- [x] Container image matches the design - FIXED in this round (fix 23): the hub image installed tmux and ttyd that architecture.md places in the agent containers

## Test Quality

- [x] Every FR has at least one test, and all of them run and pass
- [x] Tests use descriptive names: test_<what>_<when>_<expected> (fix 13); tests with several asserts check one behavior each (a response and its stored effect, or the fields of one record)
- [x] No test depends on execution order
- [x] Coverage >= 80% - 96% (`uv run pytest --cov=src --cov-report=term-missing`: 59 passed, 0 skipped); now enforced by `fail_under = 80` in pyproject.toml, CI runs with --cov (fix 20)

## Security

- [x] No secrets, passwords, or tokens in code or tests (grep: no hits)
- [x] All external inputs are validated - agent name pattern, status enum, required hook_event_name all enforced by the OpenAPI spec (probed: 400 for each); store re-validates names; --terminal accepts http(s) only
- [x] No arbitrary code execution from user input - no shell=True/eval/exec/os.system in src; dashboard renders with textContent only; bandit: no issues
- [x] No unverified binaries in the shipped image - FIXED (fix 23)

## Code Quality

- [x] No em-dashes or long-dashes in comments or strings (U+2012..U+2015, U+2212: none in src, tests, scripts, docs)
- [x] No magic numbers - named constants in dashboard and tests
- [x] No dead code - the unreachable `except ValueError` branches were replaced by explicit, tested checks (fix 21)
- [x] Functions are pure where possible
- [x] `uv run ruff check src/ tests/`: All checks passed (after fix 17); `ruff format --check`: clean

## Required Fixes (open)

None.

## Result

phase: review
status: done
output: review-checklist.md round 4 - 0 critical, 0 major, 0 minor open (all 9 round-2 minor findings fixed)

## Fix History

| Fix | Severity | State | Commit |
|---|---|---|---|
| 1 stored XSS in dashboard | critical | fixed, verified (tests green) | 3ab9bbd |
| 2 FR-08 CLI wiring (--terminal) | critical | fixed, verified | 1ea42d7 |
| 3 FR-09 test (agent-terminal.sh + tmux integration tests) | critical | fixed, verified in round 3 (4/4 pass with tmux 3.3a, after fix 24) | dd267b5 |
| 4 module globals in api/app.py | major | fixed, verified | 3ab9bbd |
| 5 NFR-04 shared tmp file | major | fixed, verified | 19e918e |
| 6 agent name validation | major | fixed, verified (incl. HTTP 400 probes) | 19e918e, 3ab9bbd |
| 7 FR-05 collectors wired | major | resolved: hook route wired, polling descoped for v1 | 3ab9bbd, e0794c5, bd3d095 |
| 8 terminal_port=None | minor | fixed (side effect of 4) | 3ab9bbd |
| 12 magic numbers | minor | fixed | 3ab9bbd |
| 14 architecture.md drift | minor | fixed | b86d404 |
| 16 duplicate requirements files | minor | fixed | 6d3ffe9 |
| 17 ruff check failed (9 errors on ruff 0.16 defaults) | major | fixed, verified | 5bbb65a |
| 18 no .gitignore | minor | fixed | 5bbb65a |
| 23 hub image installed tmux, curl and an unchecksummed ttyd binary it never uses (agent-terminal.sh is not in the image; architecture.md puts tmux+ttyd in agent containers) | major | fixed: removed from Dockerfile; image build not verified (no podman here) | this round |
| 24 FR-09 test helper used `-t =agent-1` as a pane target; tmux 3.3a rejects that ("can't find pane"), exact-match pane targets need `=agent-1:`. agent-terminal.sh itself was correct (session targets) | critical (test bug, found on first tmux run) | fixed, verified (3 consecutive green runs; mutation check) | this round |
| 9 tests for FR-04 restart, FR-06 /openapi.json, FR-07 refresh | minor | fixed, verified | round 4 |
| 10 HookAdapter: SessionStart -> idle, UserPromptSubmit/PreToolUse -> working, Notification keeps message | minor | fixed, verified (unit + API tests, live hub probe); payload shape from documented hook input, not yet a live Claude Code invocation | round 4 |
| 11 list() skips corrupt files, invalid names and files naming another agent (logged) | minor | fixed, verified | round 4 |
| 13 test names follow test_<what>_<when>_<expected> | minor | fixed | round 4 |
| 15 starlette declared as a direct dependency (>=1.6, uv.lock updated) | minor | fixed, verified | round 4 |
| 19 image: multi-stage, `uv sync --frozen --no-dev` from uv.lock, non-root user, writable /data/status | minor | fixed, verified: user built and ran the image with podman on the host (2026-11-07) | round 4 |
| 20 coverage gate: fail_under = 80 in pyproject.toml, CI runs pytest --cov | minor | fixed, verified (gate fails a run under the threshold) | round 4 |
| 21 api handlers: explicit name check + "Invalid status" instead of unreachable except branches | minor | fixed, verified (direct handler tests) | round 4 |
| 22 examples/claude-code-hooks: hook-to-hub.sh, settings.json, README; script added to CI shellcheck | minor | fixed, verified end to end against a running hub; shellcheck not run locally (not installed) | round 4 |
| 25 hub answered only on IPv4: http://localhost:8000 failed on the host (Fedora resolves localhost to ::1 first) while http://127.0.0.1:8000 worked. Found by the user on the first podman run. entrypoint.sh now binds every address (empty host), CLI default is "localhost" (127.0.0.1 and ::1); "::" alone is not dual-stack because asyncio sets IPV6_V6ONLY | major (found after round 4, fixed) | fixed, verified by tests/integration/test_listen_addresses.py; rebuilt image not yet re-run by the user | after round 4 |
