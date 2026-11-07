# Demo agent

One fake agent to see the hub working end to end: a Fedora 45 container
with a bash session in tmux, served by ttyd (attach from the dashboard), plus an `agent-status` command
that reports to the hub.

```bash
./podman_build.sh            # hub image, once
examples/demo-agent/run.sh   # builds the demo agent, restarts the hub, starts the agent
```

The dashboard shows `demo-agent` as idle. Click **attach** to open its
terminal in a new tab, then type:

```bash
agent-status working building the thing
agent-status blocked needs your approval
agent-status done
```

The dashboard row follows within about 3 seconds.

How it is wired: both containers join the podman network `agenthubctl`; the
agent reports to `http://agenthubctl:8000`; the hub is started with
`AGENTHUBCTL_TERMINALS=demo-agent=http://127.0.0.1:7681`, the agent's ttyd
port published on the host.

Stop: `podman rm -f demo-agent agenthubctl`
