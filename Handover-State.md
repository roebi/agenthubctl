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
