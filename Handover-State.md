skill: orchestrate-sw-dev-en
goal: Build agenthubctl, a hexagonal status and terminal-attach control hub for n parallel coding agent containers (Claude Code, Codex, etc.), exposing status via OpenAPI and a minimal dashboard, with full in-browser terminal attach.
current_phase: review
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
    status: blocked
    output: review-checklist.md - 3 critical, 4 major, 9 minor findings (static pass); fix loop step 2 run 2026-11-07 - pytest 40 passed / 3 skipped, coverage 91%, ruff clean after new fixes 17 (ruff errors) + 18 (.gitignore). Still blocked on - fix 3 / FR-09 tmux integration tests skipped (no tmux in container), and code-review-en re-run (fix loop step 3) not done yet
verified_clean:
  - pytest: 40 passed, 3 skipped (tmux tests), coverage 91% (Python 3.14.10, 2026-11-07)
  - ruff check src tests: clean (ruff 0.16.5); ruff format: clean
  - shellcheck: clean (entrypoint.sh, podman_build.sh, podman_run.sh)
  - zizmor: clean (ci.yml, release.yml) - workflow-lint job added to CI so this stays enforced
  - bandit: 0 issues
  - all GitHub Actions SHA-pinned and re-verified against actual release pages, not just the API
known_gaps:
  - Dockerfile never actually built - no podman available in the session that wrote it; tmux+ttyd wiring for FR-08/09 is unverified beyond the paper design
  - no end-to-end test of the attach path (container -> /agents/{name}/terminal -> real ttyd connection)
  - interval-based polling descoped for v1 (requirements.md Out of Scope) - PollAdapter and its tests removed, recoverable from git history
  - HookAdapter only handles Notification/Stop - guessed payload shape, never confirmed against a real Claude Code hook invocation
  - ttyd has no access control - explicitly out of scope for v1 in requirements.md, worth revisiting before any non-local deployment
  - repo never pushed to GitHub - no remote, no v0.1.0 tag, release.yml has never actually run
  - code-review-en blocked (static pass done, see review-checklist.md); release-sw-project-en not started (no-self-merge rule per orchestrate-sw-dev-en)
  - repo name / committer identity / sw-dev-agent-framework consolidation explicitly deferred by user to a later session
