# SPDX-License-Identifier: Apache-2.0
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from run_registry import _validate_entry


def test_valid_stdio_entry_passes():
    entry = {"name": "x", "repo_url": "https://github.com/a/b", "transport": "stdio", "launch_command": "python server.py"}
    assert _validate_entry(entry, Path("x.json")) is None


def test_valid_http_entry_passes():
    entry = {"name": "x", "repo_url": "https://github.com/a/b", "transport": "http", "url": "https://x.example.com/mcp"}
    assert _validate_entry(entry, Path("x.json")) is None


def test_missing_repo_url_fails():
    entry = {"name": "x", "transport": "http", "url": "https://x.example.com/mcp"}
    assert _validate_entry(entry, Path("x.json")) is not None


def test_stdio_missing_launch_command_fails():
    entry = {"name": "x", "repo_url": "https://github.com/a/b", "transport": "stdio"}
    assert _validate_entry(entry, Path("x.json")) is not None


def test_invalid_transport_fails():
    entry = {"name": "x", "repo_url": "https://github.com/a/b", "transport": "carrier-pigeon"}
    assert _validate_entry(entry, Path("x.json")) is not None


def test_real_seed_entries_are_all_valid():
    servers_dir = Path(__file__).resolve().parent.parent / "servers"
    import json
    for path in servers_dir.glob("*.json"):
        entry = json.loads(path.read_text())
        assert _validate_entry(entry, path) is None, f"{path.name} failed validation"
