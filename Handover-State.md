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
verified_clean:
  - pytest: 22/22 passing (Python 3.14.4)
  - shellcheck: clean (entrypoint.sh, podman_build.sh, podman_run.sh)
  - zizmor: clean (ci.yml, release.yml) - workflow-lint job added to CI so this stays enforced
  - bandit: 0 issues
  - all GitHub Actions SHA-pinned and re-verified against actual release pages, not just the API
known_gaps:
  - Dockerfile never actually built - no podman available in the session that wrote it; tmux+ttyd wiring for FR-08/09 is unverified beyond the paper design
  - no end-to-end test of the attach path (container -> /agents/{name}/terminal -> real ttyd connection)
  - PollAdapter's second agent type never chosen (Codex or other) - check_fn exists, nothing concrete calls it yet
  - HookAdapter only handles Notification/Stop - guessed payload shape, never confirmed against a real Claude Code hook invocation
  - ttyd has no access control - explicitly out of scope for v1 in requirements.md, worth revisiting before any non-local deployment
  - repo never pushed to GitHub - no remote, no v0.1.0 tag, release.yml has never actually run
  - code-review-en and release-sw-project-en phases not started (no-self-merge rule per orchestrate-sw-dev-en)
  - repo name / committer identity / sw-dev-agent-framework consolidation explicitly deferred by user to a later session
