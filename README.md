# agenthubctl

One place to see what all your coding agents are doing - and to step into
any of them.

You run n coding agents (Claude Code, Codex, ...) in parallel, each in its
own container. agenthubctl collects each agent's status - `working`,
`blocked`, `idle` or `done`, with a message - and serves it through an
OpenAPI HTTP interface and a small web dashboard. From the dashboard you
attach to any agent's live terminal in your browser.

## What it does today, and what it does not

| agenthubctl can | agenthubctl cannot (yet) |
|---|---|
| collect each agent's status and message | send input to an agent through the API |
| list all statuses, or get one agent's status | stop, restart or start agents |
| hand out each agent's terminal link | assign tasks to agents |
| let a human attach to an agent's live terminal and type | authenticate users - run it locally only |

So "controlling" an agent today means: the API tells you **which** agent
needs attention and **why**, and a human acts on it through the attached
terminal. Acting through the API itself (answering a blocked agent, sending
a prompt) is a possible next step, not part of v0.1.0.

## Use cases

### For agents

An agent - for example a Claude Code session acting as a coordinator - reads
the OpenAPI interface to know the state of the other agents: who is still
working, who is blocked and on what, who is done. It can use that to decide
what to do next, tell its human which agent is waiting, or wait until the
agents it depends on are done.

```bash
# which agents are blocked, and why?
curl -s http://localhost:8000/agents \
  | jq -r '.[] | select(.status == "blocked") | "\(.name): \(.message)"'
```

An agent also reports its **own** status the same way:

```bash
curl -X POST -H 'Content-Type: application/json' \
  -d '{"status": "working", "message": "refactoring the store"}' \
  http://localhost:8000/agents/web-dashboard/status
```

The spec at `http://localhost:8000/openapi.json` describes every operation,
so an agent can discover the interface on its own.

### For automation

Scripts, CI jobs, chat bots or a controller service use the same interface:
send a notification when an agent becomes blocked, wait in a pipeline until
all agents are done, or collect statuses for a report.

```python
import json
import time
import urllib.request

HUB = "http://localhost:8000"

def statuses():
    with urllib.request.urlopen(f"{HUB}/agents") as resp:
        return json.load(resp)

# wait until every agent is done, report blocked ones on the way
while not all(a["status"] == "done" for a in statuses()):
    for agent in statuses():
        if agent["status"] == "blocked":
            print(f"{agent['name']} is blocked: {agent['message']}")
    time.sleep(10)
```

### For humans

Open the dashboard at `http://localhost:8000/`. It lists every agent with its
status, message and last update, and refreshes every 3 seconds. Click
**attach** to open that agent's terminal in a new browser tab - the live
session, with its full scrollback, where you can type: answer the question
it is blocked on, approve a step, or take over. Closing the tab and
attaching again rejoins the same session.

## Quick start

Requires podman (or Docker with the same commands).

```bash
./podman_build.sh   # build the hub image
./podman_run.sh     # start the hub on port 8000, opens the dashboard
```

`podman_run.sh` waits until the hub answers, prints the dashboard and
OpenAPI links, and opens the dashboard in your browser on a desktop session
(`AGENTHUBCTL_OPEN_BROWSER=0` to skip). Status files are kept in the podman
volume `agenthubctl-status`, so they survive restarts.

### Try it with a demo agent

```bash
examples/demo-agent/run.sh
```

starts one demo agent next to the hub: a bash session in tmux, served by
ttyd. Attach to it from the dashboard and type
`agent-status blocked needs your approval` - the dashboard follows. See
[examples/demo-agent/README.md](examples/demo-agent/README.md).

### Without a container

```bash
uv run agenthubctl --status-dir ./status
```

serves on `http://localhost:8000`. `agenthubctl --help` lists all options.

## Connecting your agents

Each agent container does two things: it reports its status, and it serves
its terminal.

**Status from Claude Code** - forward Claude Code hooks to the hub with
[examples/claude-code-hooks/](examples/claude-code-hooks/README.md). Hook
events map to statuses: SessionStart -> idle, UserPromptSubmit and
PreToolUse -> working, Notification -> blocked (with the notification text),
Stop -> done.

**Status from any other agent** - anything that can make an HTTP call
reports directly with `POST /agents/{name}/status`.

**Terminal** - in the agent container (needs tmux and ttyd), start the agent
through `agent-terminal.sh`:

```bash
agent-terminal.sh my-agent 7681 -- claude
```

It runs the agent in a tmux session with a large scrollback and serves that
session through ttyd on port 7681. Then tell the hub where the terminal is:

```bash
agenthubctl --terminal my-agent=http://127.0.0.1:7681
# or, e.g. with podman_run.sh:
AGENTHUBCTL_TERMINALS="my-agent=http://127.0.0.1:7681 other=http://127.0.0.1:7682" ./podman_run.sh
```

The URL is what the **browser** opens, so it must be reachable from the
machine where you use the dashboard.

## API

Full specification: `GET /openapi.json`.

| Method and path | Purpose |
|---|---|
| `GET /agents` | all agent statuses |
| `GET /agents/{name}` | one agent's status (404 if unknown) |
| `POST /agents/{name}/status` | report a status: `{"status": "working\|blocked\|idle\|done", "message": "..."}` |
| `POST /agents/{name}/hook` | report a raw Claude Code hook payload |
| `GET /agents/{name}/terminal` | the agent's terminal URL (404 if none configured) |
| `GET /` | the dashboard |

A status looks like:

```json
{"name": "web-dashboard", "status": "blocked", "timestamp": "2026-11-07T16:21:48Z", "message": "needs deploy approval"}
```

Agent names are 1 to 64 characters from `A-Z a-z 0-9 . _ -`, starting with a
letter or digit.

## Configuration

| Option | Environment (container) | Default |
|---|---|---|
| `--status-dir` | `AGENTHUBCTL_STATUS_DIR` | `./status` (`/data/status` in the image) |
| `--host` | `AGENTHUBCTL_HOST` | `localhost` (every address in the image) |
| `--port` | `AGENTHUBCTL_PORT` | `8000` |
| `--terminal NAME=URL` (repeatable) | `AGENTHUBCTL_TERMINALS` (space-separated) | none |

`podman_run.sh` also reads `AGENTHUBCTL_HOST_PORT`,
`AGENTHUBCTL_STATUS_VOLUME` and `AGENTHUBCTL_OPEN_BROWSER`.

## Security

agenthubctl has **no authentication**: anyone who can reach the hub can read
and report statuses, and anyone who can reach an agent's ttyd port can type
into that agent's terminal. Run it on your own machine or a trusted network
only. Agent names and messages are always rendered as text, never as HTML.

## Development

```bash
uv run pytest --cov=src --cov-report=term-missing   # tests, 80% coverage gate
uv run ruff check src/ tests/                       # lint
```

The FR-09 integration tests need tmux. The project is built with the
[sw-dev-agent-framework](https://github.com/roebi/sw-dev-agent-framework)
process: `requirements.md`, `architecture.md`, `review-checklist.md` and
`Handover-State.md` record each phase.

## License

[MIT](LICENSE)
