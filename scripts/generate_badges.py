# SPDX-License-Identifier: Apache-2.0
"""Turns docs/registry.json into per-server shields.io endpoint-badge JSON
files (docs/badges/<name>.json) and a static docs/index.html listing every
registered server with its live badge.

A registered project embeds its badge with:
    [![MCP Conformant](https://img.shields.io/endpoint?url=https://<user>.github.io/mcp-registry/badges/<name>.json)](https://github.com/jayblast-spec/mcp-registry)
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "docs" / "registry.json"
BADGES_DIR = ROOT / "docs" / "badges"

STATUS_COLOR = {"compliant": "brightgreen", "not-compliant": "red", "error": "lightgrey"}
STATUS_MESSAGE = {"compliant": "conformant", "not-compliant": "not conformant", "error": "test error"}


def main() -> None:
    data = json.loads(REGISTRY.read_text())
    BADGES_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for server in data["servers"]:
        status = server["status"]
        badge = {
            "schemaVersion": 1,
            "label": "mcp-conform",
            "message": STATUS_MESSAGE.get(status, status),
            "color": STATUS_COLOR.get(status, "lightgrey"),
        }
        (BADGES_DIR / f"{server['name']}.json").write_text(json.dumps(badge))

        badge_url = f"https://img.shields.io/endpoint?url=https://jayblast-spec.github.io/mcp-registry/badges/{server['name']}.json"
        rows.append(
            f'<tr><td><a href="{server["repo_url"]}">{server["name"]}</a></td>'
            f'<td><img src="{badge_url}" alt="mcp-conform badge"></td>'
            f'<td>{server["detail"]}</td></tr>'
        )

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>MCP Registry</title>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:.5rem;border-bottom:1px solid #ddd;text-align:left}}</style>
</head><body>
<h1>MCP Registry</h1>
<p>Servers tested against the <a href="https://github.com/jayblast-spec/mcp-conform">mcp-conform</a> spec-compliance suite. Register your own via a pull request to <a href="https://github.com/jayblast-spec/mcp-registry">the registry repo</a>.</p>
<table><tr><th>Server</th><th>Status</th><th>Detail</th></tr>
{''.join(rows)}
</table>
</body></html>"""
    (ROOT / "docs" / "index.html").write_text(html)
    print(f"Wrote {len(data['servers'])} badge(s) and docs/index.html")


if __name__ == "__main__":
    main()
