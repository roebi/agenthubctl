# agenthubctl - project instructions

## Development process

This project is built with my skill set **sw-dev-agent-framework**
(repo roebi/sw-dev-agent-framework). The skill **orchestrate-sw-dev-en** is
the orchestrator of the whole software development process:

requirements -> design -> implement -> review -> release

Each phase runs through its sub-skill: gather-requirements-en,
design-architecture-en, apply-tdd-loop-en, code-review-en,
release-sw-project-en.

## At session start

1. Load the `orchestrate-sw-dev-en` skill.
2. Read `Handover-State.md`. Its `current_phase` and the first result with
   `status != done` say where to resume.
3. Continue that phase with its sub-skill.

## Rules

- Follow the orchestrator's phase gates: no skipping, a blocked phase stops
  and is reported, review must pass (0 critical, 0 major) before release.
- Record every phase outcome in `Handover-State.md`; review findings and
  the fix log go in `review-checklist.md`.
- Keep state in those files, not here - this file only says how we work.

## Commands

- Tests + coverage (>= 80%): `uv run pytest --cov=src --cov-report=term-missing`
- Lint: `uv run ruff check src/ tests/`

Claude runs in a podman container: check which tools exist (tmux, podman,
gh, ...) before assuming them.
