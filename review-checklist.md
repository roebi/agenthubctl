# Review Checklist

Skill: code-review-en
Reviewed commit: 62fd50f (main)
Date: 2026-11-07
Scope: STATIC PARTS ONLY. The review container has no Python, uv, pytest
or ruff, so steps 3 (coverage) and 5 (ruff) were not run, and no test was
executed in this session. "Test passes" below is "not run" everywhere; the
22/22 figure in Handover-State.md is from the implement phase and was not
re-verified here.

## Requirements Coverage

| FR | Covered by test | Test passes | Notes |
|---|---|---|---|
| FR-01 | yes | not run | test_file_store (report/get), test_hook_adapter, test_poll_adapter, test_post_agent_status_records_the_status |
| FR-02 | yes | not run | test_get_agents_returns_all_statuses, test_list_returns_all_reported_statuses |
| FR-03 | yes | not run | test_get_agent_by_name_returns_that_agent, test_get_agent_returns_404_for_unknown_agent |
| FR-04 | partial | not run | atomic write tested (no leftover tmp); survival across restart (new store instance on same dir) not tested |
| FR-05 | partial | not run | both collectors unit-tested in isolation; neither is wired into the running app, no per-agent-type selection exists (see fix 7) |
| FR-06 | partial | not run | endpoints are exercised through the spec-routed app; no test that the OpenAPI document itself is served |
| FR-07 | partial | not run | test_dashboard_route_serves_html checks HTML is served; auto-refresh not tested |
| FR-08 | partial | not run | GET /agents/{name}/terminal tested with an injected mapping; the shipped CLI wires an empty mapping, so attach always 404s (see fix 2) |
| FR-09 | no | - | no test of any kind; needs a container-level test (tmux + ttyd) |

## Architecture Compliance

- [x] Module structure matches architecture.md (extra tests/unit/test_cli.py and test_models.py are justified; doc drift noted in fix 14)
- [x] No module has more than one responsibility
- [ ] Side effects are isolated per design - api/app.py keeps module-level globals, contradicting "factory, no globals" (fix 4)

## Test Quality

- [ ] Every FR has at least one test - FR-09 has none
- [ ] Tests use descriptive names: test_<what>_<when>_<expected> - most omit the <when> part
- [x] No test depends on execution order - holds today only because every test calls create_app again; latent risk via the globals in fix 4
- [ ] Coverage >= 80% - NOT RUN (no uv/pytest in the review container)

## Security

- [x] No secrets, passwords, or tokens in code or tests (grep for password|secret|token|key = : no hits)
- [ ] All external inputs are validated - agent name path parameter has no pattern; status message is rendered unescaped (fixes 1, 6)
- [ ] No arbitrary code execution from user input - stored XSS in the dashboard (fix 1); no subprocess, shell=True, eval or exec in src/

## Code Quality

- [x] No em-dashes or long-dashes in comments or strings (U+2013/2014 grep: OK; U+2012/2015/2212 also checked: none)
- [ ] No magic numbers - use named constants (fix 12)
- [ ] No dead code - HookAdapter and PollAdapter are unreachable from the shipped app (fix 7)
- [x] Functions are pure where possible
- [ ] ruff check src/ tests/ - NOT RUN (no uv/ruff in the review container)

## Required Fixes

1. Stored XSS: dashboard builds rows with innerHTML from agent.name and agent.message; anyone who can POST /agents/{name}/status (unauthenticated) injects script into every viewer's dashboard. Build cells with textContent and encodeURIComponent the name in the terminal fetch URL - src/agenthubctl/dashboard/static/index.html:35-41,48 - severity: critical
2. FR-08 not usable in the shipped product: cli.py wires TtydTerminalAdapter(endpoints={}) with no option to configure endpoints, so every attach click returns 404 - src/agenthubctl/cli.py:25 - severity: critical
3. Missing test for FR-09 (scrollback / rendering on attach); no test at any level - tests/ - severity: critical
4. Architecture violation: create_app stores the ports in module globals (_status_port, _terminal_port); a second create_app call silently rewires the first app. Bind ports per app instead (e.g. Connexion resolver or closures) - src/agenthubctl/api/app.py:12-13,40-42 - severity: major
5. NFR-04 not guaranteed under concurrency: the tmp file name is fixed (<id>.json.tmp), so two writers for the same agent (hook + POST, or two POSTs) share it and one can os.replace the other's half-written file into place. Use a unique tmp file in the same dir (tempfile.NamedTemporaryFile(dir=..., delete=False)) and fsync before os.replace - src/agenthubctl/adapters/store/file_store.py:31-33 - severity: major
6. Agent name is never validated: the store builds base_dir / f"{agent_id}.json" from it, so an id like "../x" writes outside base_dir when it reaches the store from any caller; the OpenAPI path parameter has no pattern either (HTTP exploitability not verified without running). Add a name pattern (e.g. ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$) in openapi.json and enforce it in FileStatusStore - src/agenthubctl/adapters/store/file_store.py:15, src/agenthubctl/api/openapi.json (all {name} parameters) - severity: major
7. FR-05 only half-implemented / dead code: HookAdapter and PollAdapter are not reachable from cli.py or api/app.py, and there is no per-agent-type selection. Wire them (e.g. hook POST route or CLI hook subcommand, poll loop started by serve) or record the descoping in requirements.md - src/agenthubctl/cli.py, src/agenthubctl/adapters/collectors/ - severity: major
8. create_app accepts terminal_port=None, then get_agent_terminal calls None.resolve -> 500; the API test fixture relies on passing None - src/agenthubctl/api/app.py:33,39, tests/api/test_agents_endpoints.py:14 - severity: minor
9. Add tests: FR-04 restart (second FileStatusStore on the same dir reads the status), FR-06 OpenAPI document served, FR-07 dashboard contains the refresh loop - tests/ - severity: minor
10. HookAdapter never reports working or idle and silently drops unknown events, so an agent stays "blocked" until Stop (known open question: real hook payload shape) - src/agenthubctl/adapters/collectors/hook_adapter.py:10-15 - severity: minor
11. One corrupt or foreign *.json file in the status dir makes list() raise, so GET /agents and the whole dashboard return 500 - src/agenthubctl/adapters/store/file_store.py:41-45 - severity: minor
12. Magic numbers: poll interval default 5, dashboard refresh 3000 ms - src/agenthubctl/adapters/collectors/poll_adapter.py:14, src/agenthubctl/dashboard/static/index.html:58 - severity: minor
13. Test hygiene: names lack <when>; several tests assert more than one thing; FakeStatusPort duplicated in two files (move to tests/conftest.py); API terminal tests repeat setup instead of a fixture - tests/unit/test_hook_adapter.py:5, tests/unit/test_poll_adapter.py:5, tests/api/test_agents_endpoints.py:48-73 - severity: minor
14. Doc drift in architecture.md: resolve returns str | None not TerminalEndpoint; report has a timestamp parameter; HookAdapter takes agent_id - architecture.md (Components) - severity: minor
15. starlette is imported directly but only present as a transitive dependency of connexion; declare it - src/agenthubctl/api/app.py:4, pyproject.toml - severity: minor
16. requirements.md and REQUIREMENTS.md both exist with different ID schemes (FR-xx vs R-xxx, which commit messages still cite) and collide on case-insensitive filesystems; keep one - requirements.md, REQUIREMENTS.md - severity: minor

## Result

phase: review
status: blocked
output: review-checklist.md - 3 critical, 4 major, 9 minor findings (static parts only; coverage, ruff and test runs still open)
