"""FR-09: attaching to an agent terminal joins the live tmux session with its
full scrollback - not a new shell and not a replay.

These run the real agent-terminal.sh against a real, isolated tmux server.
ttyd is replaced by "echo" (TTYD_BIN) so the test can check exactly what ttyd
would be told to run for each browser client.
"""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "agent-terminal.sh"
SESSION = "agent-1"
TTYD_PORT = "7681"
TMUX_DEFAULT_HISTORY_LIMIT = 2000
LINES_PRINTED = TMUX_DEFAULT_HISTORY_LIMIT + 1000
WAIT_TIMEOUT_SECONDS = 10
WAIT_STEP_SECONDS = 0.1
AGENT_LIFETIME_SECONDS = "60"

requires_tmux = pytest.mark.skipif(shutil.which("tmux") is None, reason="tmux not installed")


@pytest.fixture
def tmux_env():
    # short dir on purpose: tmux's socket path must fit in a unix socket name
    socket_dir = tempfile.mkdtemp(prefix="at-")
    env = {**os.environ, "TMUX_TMPDIR": socket_dir, "TTYD_BIN": "echo"}
    env.pop("TMUX", None)
    yield env
    subprocess.run(["tmux", "kill-server"], env=env, capture_output=True)
    shutil.rmtree(socket_dir, ignore_errors=True)


def run_script(env, *args):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        env=env,
        capture_output=True,
        text=True,
        timeout=WAIT_TIMEOUT_SECONDS,
    )


def tmux(env, *args):
    return subprocess.run(
        ["tmux", *args], env=env, capture_output=True, text=True, check=True
    ).stdout


def wait_for_pane_text(env, text):
    deadline = time.monotonic() + WAIT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if text in tmux(env, "capture-pane", "-p", "-S", "-", "-t", f"={SESSION}"):
            return
        time.sleep(WAIT_STEP_SECONDS)
    raise AssertionError(f"{text!r} never appeared in the tmux pane")


def test_agent_terminal_without_command_exits_with_usage_error(tmp_path):
    result = run_script({**os.environ, "TMUX_TMPDIR": str(tmp_path)}, SESSION, TTYD_PORT)

    assert result.returncode == 2


@requires_tmux
def test_agent_terminal_serves_a_writable_attach_to_the_existing_session(tmux_env):
    result = run_script(tmux_env, SESSION, TTYD_PORT, "--", "sleep", AGENT_LIFETIME_SECONDS)

    assert result.returncode == 0
    assert result.stdout.split() == [
        "--port", TTYD_PORT, "--writable", "tmux", "attach-session", "-t", f"={SESSION}",
    ]


@requires_tmux
def test_agent_terminal_keeps_scrollback_beyond_tmux_default_history(tmux_env):
    command = f"seq 1 {LINES_PRINTED}; sleep {AGENT_LIFETIME_SECONDS}"
    run_script(tmux_env, SESSION, TTYD_PORT, "--", "sh", "-c", command)
    wait_for_pane_text(tmux_env, str(LINES_PRINTED))

    history = tmux(tmux_env, "capture-pane", "-p", "-S", "-", "-t", f"={SESSION}")
    lines = [line for line in history.splitlines() if line.strip()]

    assert lines[0] == "1"
    assert lines[-1] == str(LINES_PRINTED)


@requires_tmux
def test_agent_terminal_when_run_again_reuses_the_running_agent(tmux_env):
    run_script(tmux_env, SESSION, TTYD_PORT, "--", "sleep", AGENT_LIFETIME_SECONDS)
    first_pid = tmux(tmux_env, "display-message", "-p", "-t", f"={SESSION}", "#{pane_pid}")

    run_script(tmux_env, SESSION, TTYD_PORT, "--", "sleep", AGENT_LIFETIME_SECONDS)
    second_pid = tmux(tmux_env, "display-message", "-p", "-t", f"={SESSION}", "#{pane_pid}")

    assert second_pid == first_pid
    assert tmux(tmux_env, "list-sessions", "-F", "#{session_name}").split() == [SESSION]
