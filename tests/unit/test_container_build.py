"""The hub image builds the package from the files the Dockerfile copies.
Every file pyproject.toml references (readme, license-files) must be among
them, or `uv sync` inside the image fails although the local build passes.
"""

import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def copied_into_build_stage():
    copied = set()
    for line in (REPO / "Dockerfile").read_text().splitlines():
        parts = line.split()
        if parts[:1] == ["COPY"] and not any(p.startswith("--") for p in parts):
            copied.update(parts[1:-1])
    return copied


def test_dockerfile_when_building_copies_every_file_pyproject_references():
    project = tomllib.loads((REPO / "pyproject.toml").read_text())["project"]
    referenced = {project["readme"], *project["license-files"]}

    assert referenced <= copied_into_build_stage()
