skill: orchestrate-sw-dev-en
goal: Build agenthubctl, a hexagonal status and terminal-attach control hub for n parallel coding agent containers (Claude Code, Codex, etc.), exposing status via OpenAPI and a minimal dashboard, with full in-browser terminal attach.
current_phase: release
results:
  - phase: requirements
    status: done
    output: requirements.md written with 9 functional and 5 non-functional requirements
  - phase: design
    status: done
    output: architecture.md written - 10 components, 4 open questions, 1 corrected during implement
  - phase: implement
    status: done
    output: apply-tdd-loop-en complete - 9/9 FRs, 22 passing tests on Python 3.14, 2 honesty corrections logged in TDD Handover-State history
  - phase: review
    status: done
    output: review-checklist.md round 4 - 0 critical, 0 major, 0 minor open; fix 3 verified with tmux 3.3a after fix 24; all 9 minor findings fixed; pytest 59 passed / 0 skipped, coverage 96%, ruff clean
  - phase: release
    status: pending
    output: not started - decided: name stays agenthubctl, user creates the GitHub repo, identity Robert Halter <roebi@users.noreply.github.com> (all commits carry it), remote origin https://github.com/roebi/agenthubctl (created by the user, empty, first push by the user); open: PyPI vs GitHub Release only
verified_clean:
  - pytest: 61 passed, 0 skipped, coverage 96%, 80% gate enforced via fail_under (Python 3.14.10, tmux 3.3a, 2026-11-07)
  - ruff check src tests: clean (ruff 0.16.5); ruff format: clean
  - shellcheck: clean on all 8 scripts (ShellCheck 0.11.0 via `uvx --from shellcheck-py shellcheck`, and CI)
  - zizmor: clean (ci.yml, release.yml) - workflow-lint job added to CI so this stays enforced
  - bandit: 0 issues (re-run 2026-11-07)
  - all GitHub Actions SHA-pinned and re-verified against actual release pages, not just the API
known_gaps:
  - Dockerfile built and run by the user with podman on the host (2026-11-07); fixes 25 (IPv6/localhost) and 28 (attach link) confirmed there; hub image only (no tmux/ttyd), multi-stage uv sync --frozen, non-root (fix 19); agent containers must bring tmux + ttyd + agent-terminal.sh (+ examples/claude-code-hooks) themselves
  - attach path verified manually on the host with examples/demo-agent (dashboard -> real ttyd terminal -> agent-status back to the dashboard, re-attach keeps the session and its output, 2026-11-07); no automated end-to-end test of it
  - interval-based polling descoped for v1 (requirements.md Out of Scope) - PollAdapter and its tests removed, recoverable from git history
  - HookAdapter maps SessionStart/UserPromptSubmit/PreToolUse/Notification/Stop from the documented hook input - not yet confirmed against a live Claude Code hook invocation
  - ttyd has no access control - explicitly out of scope for v1 in requirements.md, worth revisiting before any non-local deployment
  - remote origin set to https://github.com/roebi/agenthubctl but not pushed yet - no v0.1.0 tag, release.yml has never actually run
  - release-sw-project-en not started
  - sw-dev-agent-framework consolidation explicitly deferred by user to a later session
