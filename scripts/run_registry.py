# SPDX-License-Identifier: Apache-2.0
"""Runs mcp-conform against every entry in servers/*.json.

For a "stdio" entry: clones repo_url into a temp dir, creates a dedicated
virtualenv for it, runs setup_commands inside that venv, then hands
mcp-conform a launch_command run with the venv's own python — never the
ambient interpreter this script itself runs under.

Why the isolation matters, concretely: a registered project's own
setup_commands might install itself in editable mode ("pip install -e .")
or otherwise mutate the active Python environment. Running that in the same
environment mcp-conform depends on can — and during development of this
script, did — break mcp-conform's own installation. Every entry gets its
own throwaway venv so one project's setup can never affect another's test,
or this tool's own.

For an "http" entry: hands mcp-conform the url directly, no cloning, no venv.

Writes results to docs/registry.json (the source of truth the badge
generator and the static site both read) and prints a human summary.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

from mcp_conform.runner import run
import asyncio

ROOT = Path(__file__).resolve().parent.parent
SERVERS_DIR = ROOT / "servers"
OUTPUT = ROOT / "docs" / "registry.json"

REQUIRED_COMMON = ("name", "repo_url", "transport")
REQUIRED_BY_TRANSPORT = {
    "http": ("url",),
    "stdio": ("launch_command",),
}


def _validate_entry(entry: dict, source: Path) -> str | None:
    """Returns an error message if the entry is malformed, else None."""
    missing = [k for k in REQUIRED_COMMON if not entry.get(k)]
    if missing:
        return f"{source.name}: missing required field(s) {missing}"
    transport = entry["transport"]
    if transport not in REQUIRED_BY_TRANSPORT:
        return f"{source.name}: transport must be 'stdio' or 'http', got {transport!r}"
    missing = [k for k in REQUIRED_BY_TRANSPORT[transport] if not entry.get(k)]
    if missing:
        return f"{source.name}: transport {transport!r} requires field(s) {missing}"
    return None


def _venv_python(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _clone_and_setup(entry: dict, workdir: Path) -> tuple[Path, Path]:
    """Clones the repo and builds a dedicated venv for it. Returns
    (clone_dir, venv_python_path)."""
    clone_dir = workdir / "repo"
    subprocess.run(["git", "clone", "--depth", "1", entry["repo_url"], str(clone_dir)], check=True, capture_output=True)

    venv_dir = workdir / "venv"
    venv.create(venv_dir, with_pip=True)
    venv_python = _venv_python(venv_dir)

    # Put the venv's own bin/Scripts dir first on PATH so a setup command
    # that just says "pip install ..." (not "python -m pip install ...")
    # still resolves to this venv's pip, not whatever "pip" is ambient.
    env = os.environ.copy()
    venv_bin = str(venv_python.parent)
    env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
    env["VIRTUAL_ENV"] = str(venv_dir)

    for cmd in entry.get("setup_commands", []):
        subprocess.run(cmd, shell=True, cwd=clone_dir, check=True, capture_output=True, env=env)
    return clone_dir, venv_python


def _rewrite_for_venv(launch_command: str, venv_python: Path) -> str:
    """A launch_command like "python server.py" must run under the entry's
    own isolated venv, not whatever Python this script happens to run
    under."""
    parts = launch_command.split(" ", 1)
    if parts[0] in ("python", "python3"):
        return f'"{venv_python}" {parts[1] if len(parts) > 1 else ""}'.strip()
    return launch_command


async def _test_entry(entry: dict) -> dict:
    result = {
        "name": entry["name"], "repo_url": entry["repo_url"], "transport": entry["transport"],
        "status": "error", "pass": 0, "fail": 0, "warn": 0, "skip": 0, "detail": "",
    }
    try:
        if entry["transport"] == "http":
            report = await run(entry["url"])
            return _summarize(entry, report)

        with tempfile.TemporaryDirectory() as tmp:
            clone_dir, venv_python = _clone_and_setup(entry, Path(tmp))
            target = _rewrite_for_venv(entry["launch_command"], venv_python)
            report = await run(target, cwd=str(clone_dir))
            return _summarize(entry, report)
    except subprocess.CalledProcessError as exc:
        result["detail"] = f"setup command failed ({exc.cmd!r}): {exc.stderr.decode(errors='replace')[:300]}"
        return result
    except Exception as exc:  # noqa: BLE001
        result["detail"] = f"{type(exc).__name__}: {exc}"
        return result


def _summarize(entry: dict, report) -> dict:
    counts = {"pass": 0, "fail": 0, "warn": 0, "skip": 0, "error": 0}
    for r in report.results:
        counts[r.status.value.lower()] += 1
    overall = "compliant" if counts["fail"] == 0 and counts["error"] == 0 else "not-compliant"
    return {
        "name": entry["name"], "repo_url": entry["repo_url"], "transport": entry["transport"],
        "status": overall, **counts,
        "detail": f"{counts['pass']} passed, {counts['fail']} failed, {counts['warn']} warned, {counts['skip']} skipped",
    }


async def main() -> int:
    results = []
    for path in sorted(SERVERS_DIR.glob("*.json")):
        try:
            entry = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            print(f"Skipping {path.name}: invalid JSON ({exc})")
            results.append({"name": path.stem, "repo_url": "", "transport": "", "status": "error",
                             "pass": 0, "fail": 0, "warn": 0, "skip": 0, "error": 1, "detail": f"invalid JSON: {exc}"})
            continue

        error = _validate_entry(entry, path)
        if error:
            print(f"Skipping {path.name}: {error}")
            results.append({"name": entry.get("name", path.stem), "repo_url": entry.get("repo_url", ""),
                             "transport": entry.get("transport", ""), "status": "error",
                             "pass": 0, "fail": 0, "warn": 0, "skip": 0, "error": 1, "detail": error})
            continue

        print(f"Testing {entry['name']}...", flush=True)
        result = await _test_entry(entry)
        print(f"  -> {result['status']}: {result.get('detail', '')}")
        results.append(result)

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps({"servers": results}, indent=2))

    any_error = any(r["status"] == "error" for r in results)
    return 1 if any_error else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
