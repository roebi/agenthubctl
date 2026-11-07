# Code Review Checklist

Skill: code-review-en
Round: 2 (re-review after the round-1 fix loop)
Reviewed commit: 57ecb4c (main), plus fix 23 below
Date: 2026-11-07
Environment: Python 3.14.10, uv, ruff 0.16.5, bandit (via uvx). No tmux,
no shellcheck, no podman in this container. Round 1 (static only, commit
62fd50f) is in git history; its fixes are summarized under Fix History.

## Requirements Coverage

| FR | Covered by test | Test passes | Notes |
|---|---|---|---|
| FR-01 | yes | yes | test_report_then_get_returns_the_reported_status, test_post_agent_status_records_the_status, test_hook_adapter_* |
| FR-02 | yes | yes | test_get_agents_returns_all_statuses, test_list_returns_all_reported_statuses |
| FR-03 | yes | yes | test_get_agent_by_name_returns_that_agent, test_get_agent_returns_404_for_unknown_agent, test_get_agent_with_invalid_name_returns_400 |
| FR-04 | partial | yes | atomic write + concurrent tmp file tested; survival across restart verified by a manual probe (second app on the same dir reads the status) but not by a test (fix 9) |
| FR-05 | yes | yes | test_post_hook_notification/stop/unknown_event_*; direct POST route tested; polling descoped for v1 in requirements.md |
| FR-06 | partial | yes | all endpoints exercised through the spec-routed app; GET /openapi.json returns 200 in a manual probe, no test (fix 9) |
| FR-07 | partial | yes | dashboard served, XSS-safe rendering asserted; auto-refresh not asserted (fix 9) |
| FR-08 | yes | yes | test_build_app_when_terminal_configured_serves_its_url (real CLI wiring), terminal 200/404 API tests, --terminal parsing incl. javascript: rejection; AGENTHUBCTL_TERMINALS env var splitting verified by manual probe |
| FR-09 | yes | NOT RUN | 3 of 4 tests in tests/integration/test_agent_terminal.py skip ("tmux not installed"); only the usage-error test ran (fix 3) |

## Architecture Compliance

- [x] Module structure matches architecture.md (extra test_cli.py, test_models.py justified)
- [x] No module has more than one responsibility
- [x] Side effects are isolated per design - create_app binds ports in closures, verified by test_two_apps_when_created_with_different_stores_stay_independent
- [x] Container image matches the design - FIXED in this round (fix 23): the hub image installed tmux and ttyd that architecture.md places in the agent containers

## Test Quality

- [x] Every FR has at least one test (FR-09 tests exist but are not yet executed, see fix 3)
- [ ] Tests use descriptive names: test_<what>_<when>_<expected> - many still omit <when> (fix 13)
- [x] No test depends on execution order
- [x] Coverage >= 80% - 91% (`uv run pytest --cov=src --cov-report=term-missing`: 40 passed, 3 skipped)

## Security

- [x] No secrets, passwords, or tokens in code or tests (grep: no hits)
- [x] All external inputs are validated - agent name pattern, status enum, required hook_event_name all enforced by the OpenAPI spec (probed: 400 for each); store re-validates names; --terminal accepts http(s) only
- [x] No arbitrary code execution from user input - no shell=True/eval/exec/os.system in src; dashboard renders with textContent only; bandit: no issues
- [x] No unverified binaries in the shipped image - FIXED (fix 23)

## Code Quality

- [x] No em-dashes or long-dashes in comments or strings (U+2012..U+2015, U+2212: none in src, tests, scripts, docs)
- [x] No magic numbers - named constants in dashboard and tests
- [x] No dead code reachable-wise, with one caveat: the `except ValueError -> 400` branches in api/app.py are unreachable through HTTP because Connexion validates the name first (fix 21, kept as defense in depth)
- [x] Functions are pure where possible
- [x] `uv run ruff check src/ tests/`: All checks passed (after fix 17); `ruff format --check`: clean

## Required Fixes (open)

3. FR-09 integration tests never executed - tmux missing in the review container, 3 tests skip. Fixed in code in round 1; needs one green run with tmux - tests/integration/test_agent_terminal.py - severity: critical (unverified)
9. Add tests: FR-04 restart (second FileStatusStore on the same dir), FR-06 GET /openapi.json served, FR-07 dashboard contains the refresh loop - all three behaviors were confirmed by manual probes - tests/ - severity: minor
10. HookAdapter never reports working or idle and drops the Notification message; real hook payload shape still unconfirmed (architecture.md open question) - src/agenthubctl/adapters/collectors/hook_adapter.py:10-15 - severity: minor
11. list() trusts every *.json in the status dir: one corrupt file makes GET /agents return 500 (probed), and a foreign file whose content names another agent produces a duplicate entry (probed) - src/agenthubctl/adapters/store/file_store.py:57-61 - severity: minor
13. Test hygiene: many names lack <when>; several tests assert more than one thing - tests/ - severity: minor
15. starlette is imported directly but only present as a transitive dependency of connexion; declare it - src/agenthubctl/api/app.py:6, pyproject.toml - severity: minor
19. Image build ignores uv.lock (`pip install .` resolves fresh, unpinned versions) and runs as root - Dockerfile - severity: minor
20. CI runs `uv run pytest` without coverage or `--cov-fail-under=80`, so the 80% gate is only enforced by this review - .github/workflows/ci.yml:27 - severity: minor
21. `except ValueError` branches in api/app.py (lines 38-39, 49-50, 56-57) are unreachable over HTTP and untested; in report_agent_status a ValueError from StatusValue(...) would be mislabeled "Invalid agent name" if spec validation were ever bypassed - src/agenthubctl/api/app.py - severity: minor
22. No shipped example of how an agent container sends Claude Code hooks to the hub (e.g. a hook command posting stdin to /agents/NAME/hook) - docs - severity: minor

## Result

phase: review
status: blocked
output: review-checklist.md round 2 - 1 critical (fix 3, unverified only: needs a tmux run), 0 major open (fix 23 found and fixed this round), 8 minor findings

## Fix History

| Fix | Severity | State | Commit |
|---|---|---|---|
| 1 stored XSS in dashboard | critical | fixed, verified (tests green) | 3ab9bbd |
| 2 FR-08 CLI wiring (--terminal) | critical | fixed, verified | 1ea42d7 |
| 3 FR-09 test (agent-terminal.sh + tmux integration tests) | critical | fixed, UNVERIFIED (tmux missing) | dd267b5 |
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
