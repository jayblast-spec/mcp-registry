<div align="center">

# mcp-registry

### Live Conformance Badges For MCP Servers

A public registry of MCP servers, each continuously tested against the [Model Context Protocol](https://modelcontextprotocol.io) spec using [mcp-conform](https://github.com/jayblast-spec/mcp-conform). Register your server with a pull request and get a live badge that shows the truth — pass or fail — not a self-reported claim.

<p>
  <a href="https://github.com/jayblast-spec/mcp-registry/actions/workflows/registry.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/jayblast-spec/mcp-registry/registry.yml?branch=master&style=for-the-badge&logo=githubactions&logoColor=white&label=Registry&color=1D4ED8"></a>
  <a href="https://github.com/jayblast-spec/mcp-registry"><img alt="GitHub Repo" src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white"></a>
</p>

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python%203.10+-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="MCP" src="https://img.shields.io/badge/Model%20Context%20Protocol-1D4ED8?style=flat-square&logo=anthropic&logoColor=white">
  <img alt="GitHub Pages" src="https://img.shields.io/badge/GitHub%20Pages-222222?style=flat-square&logo=githubpages&logoColor=white">
  <img alt="GitHub Actions" src="https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white">
  <img alt="Apache 2.0" src="https://img.shields.io/badge/Apache%202.0-1D4ED8?style=flat-square&logo=apache&logoColor=white">
</p>

<p>
  <img alt="Animated mcp-registry headline" src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=18&duration=2600&pause=650&color=1D4ED8&center=true&vCenter=true&width=760&lines=A+badge+that+means+something;Tested+daily%2C+not+claimed+once;Register+with+a+pull+request;The+truth%2C+not+a+self-report">
</p>

</div>

## What It Does

Every entry in `servers/*.json` is a real MCP server (stdio or Streamable HTTP). A GitHub Actions workflow clones or connects to each one, runs the full [mcp-conform](https://github.com/jayblast-spec/mcp-conform) spec-compliance suite against it, and publishes the result as a live shields.io badge — `conformant` (green) or `not conformant` (red), re-tested daily so a badge reflects the server's *current* state, not the state it was in the day it was submitted.

## How It Works

- `servers/*.json` — one file per registered server; see [`servers/SCHEMA.md`](servers/SCHEMA.md) for the format.
- `scripts/run_registry.py` — for a `stdio` entry, clones the repo, runs its setup commands, and launches it via mcp-conform's `run(target, cwd=...)`; for an `http` entry, calls the URL directly. Writes `docs/registry.json`.
- `scripts/generate_badges.py` — turns `docs/registry.json` into per-server shields.io endpoint-badge JSON (`docs/badges/<name>.json`) and a static `docs/index.html` listing every server.
- `.github/workflows/registry.yml` — runs the above on every push, every pull request (without publishing — a PR just reports the result, it doesn't get to overwrite the live badges), and on a daily schedule, then publishes `docs/` to GitHub Pages.

## Register Your Server

1. Fork this repo.
2. Add `servers/<your-server-name>.json` following [`servers/SCHEMA.md`](servers/SCHEMA.md).
3. Open a pull request — CI runs mcp-conform against it automatically and reports the result.
4. Once merged, embed your live badge:

```markdown
[![MCP Conformant](https://img.shields.io/endpoint?url=https://jayblast-spec.github.io/mcp-registry/badges/<your-server-name>.json)](https://github.com/jayblast-spec/mcp-registry)
```

A `not conformant` result is not rejected — the registry's job is to report the truth, not to gatekeep entry.

## Live Registry

[jayblast-spec.github.io/mcp-registry](https://jayblast-spec.github.io/mcp-registry)

## Tech Stack

| Layer | Technology |
|---|---|
| Compliance testing | [mcp-conform](https://github.com/jayblast-spec/mcp-conform) |
| Language | Python 3.10+ |
| CI / scheduled re-testing | GitHub Actions |
| Hosting | GitHub Pages (zero cost, no separate infrastructure) |
| Badges | shields.io endpoint badges |

## License

Apache 2.0 — see [LICENSE](./LICENSE).

<div align="center">

<img alt="Footer" src="https://capsule-render.vercel.app/api?type=rect&height=60&color=0:1D4ED8,55:0B1E3D,100:020617&text=michael%40arknet.digital&fontColor=FAFAFA&fontSize=18&fontAlign=50&animation=fadeIn">

</div>
