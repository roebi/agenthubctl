"""The hub must answer on both IPv4 and IPv6, because "localhost" resolves to
::1 first on many hosts (e.g. Fedora). Binding 0.0.0.0 or 127.0.0.1 alone made
http://localhost:8000 fail while http://127.0.0.1:8000 worked.

These start the real CLI in a subprocess and connect over each address family.
"""

import socket
import subprocess
import sys
import time
import urllib.request

import pytest

STARTUP_TIMEOUT_SECONDS = 15
POLL_STEP_SECONDS = 0.2
REQUEST_TIMEOUT_SECONDS = 1


def has_ipv6_loopback():
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
            sock.bind(("::1", 0))
        return True
    except OSError:
        return False


requires_ipv6 = pytest.mark.skipif(
    not has_ipv6_loopback(), reason="no IPv6 loopback on this host"
)


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def status_code(url):
    try:
        with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS) as resp:
            return resp.status
    except OSError:
        return None


@pytest.fixture
def start_hub(tmp_path):
    processes = []

    def start(*host_args):
        port = free_port()
        cmd = [sys.executable, "-m", "agenthubctl.cli", "--port", str(port)]
        cmd += ["--status-dir", str(tmp_path), *host_args]
        process = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        processes.append(process)
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if status_code(f"http://127.0.0.1:{port}/agents") == 200:
                return port
            time.sleep(POLL_STEP_SECONDS)
        raise AssertionError("hub never answered on 127.0.0.1")

    yield start
    for process in processes:
        process.terminate()
        process.wait(timeout=STARTUP_TIMEOUT_SECONDS)


@requires_ipv6
def test_cli_with_default_host_answers_on_ipv6_loopback(start_hub):
    port = start_hub()

    assert status_code(f"http://[::1]:{port}/agents") == 200


@requires_ipv6
def test_cli_with_empty_host_answers_on_ipv6_loopback(start_hub):
    # the container entrypoint's default: listen on every address, v4 and v6
    port = start_hub("--host", "")

    assert status_code(f"http://[::1]:{port}/agents") == 200
