# Registry Entry Schema

One JSON file per registered MCP server in `servers/<name>.json`:

```json
{
  "name": "human-readable-name",
  "repo_url": "https://github.com/owner/repo",
  "transport": "stdio",
  "setup_commands": ["pip install -r requirements.txt"],
  "launch_command": "python server.py",
  "url": null
}
```

- `transport`: `"stdio"` (the registry clones `repo_url`, runs `setup_commands` in it, then launches `launch_command` as a subprocess) or `"http"` (the registry calls `url` directly — no cloning, but the server must already be running somewhere reachable).
- For `"http"` entries, `setup_commands` and `launch_command` are omitted and `url` is required instead.
- Adding an entry is a pull request. CI runs `mcp-conform` against it automatically and comments the result on the PR — an entry with a `FAIL` can still be merged (the registry's job is to report the truth, not to gatekeep), but its badge will honestly show `not-compliant`.
