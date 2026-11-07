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
    output: not started - needs user decisions first (repo name, committer identity, GitHub remote, PyPI Trusted Publishing)
verified_clean:
  - pytest: 59 passed, 0 skipped, coverage 96%, 80% gate enforced via fail_under (Python 3.14.10, tmux 3.3a, 2026-11-07)
  - ruff check src tests: clean (ruff 0.16.5); ruff format: clean
  - shellcheck: clean (entrypoint.sh, podman_build.sh, podman_run.sh)
  - zizmor: clean (ci.yml, release.yml) - workflow-lint job added to CI so this stays enforced
  - bandit: 0 issues (re-run 2026-11-07)
  - all GitHub Actions SHA-pinned and re-verified against actual release pages, not just the API
known_gaps:
  - Dockerfile never actually built - no podman in any session so far; hub image only (no tmux/ttyd), multi-stage uv sync --frozen, non-root (fix 19); agent containers must bring tmux + ttyd + agent-terminal.sh (+ examples/claude-code-hooks) themselves
  - no end-to-end test of the attach path (container -> /agents/{name}/terminal -> real ttyd connection)
  - interval-based polling descoped for v1 (requirements.md Out of Scope) - PollAdapter and its tests removed, recoverable from git history
  - HookAdapter maps SessionStart/UserPromptSubmit/PreToolUse/Notification/Stop from the documented hook input - not yet confirmed against a live Claude Code hook invocation
  - ttyd has no access control - explicitly out of scope for v1 in requirements.md, worth revisiting before any non-local deployment
  - repo never pushed to GitHub - no remote, no v0.1.0 tag, release.yml has never actually run
  - release-sw-project-en not started
  - repo name / committer identity / sw-dev-agent-framework consolidation explicitly deferred by user to a later session
