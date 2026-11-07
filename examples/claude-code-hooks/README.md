# Claude Code hooks -> agenthubctl

How an agent container running Claude Code reports its status to the hub.

1. Copy `hook-to-hub.sh` into the agent image as
   `/usr/local/bin/hook-to-hub.sh` (needs `bash` and `curl`).
2. Merge `settings.json` into the agent's Claude Code settings
   (`~/.claude/settings.json` or the project's `.claude/settings.json`).
3. Start the agent container with:
   - `AGENTHUBCTL_URL` - the hub's base URL, e.g. `http://agenthubctl:8000`
   - `AGENTHUBCTL_AGENT` - the agent's name as shown on the dashboard

| Hook event | Status on the hub |
|---|---|
| SessionStart | idle |
| UserPromptSubmit, PreToolUse | working |
| Notification | blocked (with the notification text as message) |
| Stop | done |

Other events are accepted and ignored. Agent types without Claude Code
hooks can report directly:
`curl -X POST -H 'Content-Type: application/json' -d '{"status":"working"}' "$AGENTHUBCTL_URL/agents/$AGENTHUBCTL_AGENT/status"`

Not yet confirmed against a live Claude Code hook invocation: the mapping
relies on `hook_event_name` and, for Notification, `message` from the
documented hook input.
