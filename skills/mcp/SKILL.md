---
name: mcp
description: Token-efficient MCP client CLI for Pi — search, describe, and call tools across 9 configured MCP servers (E-muse-direct, KSHT, exa, firecrawl, context7, inspo, openai-docs, anthropic-docs, xai-docs). Use when a task needs web search/scraping, docs lookup, or any MCP-provided capability; workflow is mcp search/ssearch -> describe -> call.
---

# MCP Adapter

Token-efficient MCP client for Pi. Inspired by `nicobailon/pi-mcp-adapter`,
rebuilt as a plain CLI so it runs on this system via `muse.exec`.

## The pattern (important)

Do NOT dump every MCP tool definition into context. Work in this order:

1. `mcp search <keywords>` — find candidate tools across all servers (uses disk cache).
   `mcp ssearch <natural-language query>` — semantic search instead: asks Jev
   which tool best matches (cross-lingual, e.g. Vietnamese query vs English
   tool names), ranked with probabilities; abstains when nothing fits.
2. `mcp describe <server> <tool>` — read the one tool's input schema
3. `mcp call <server> <tool> --args '{...}'` — run it

Servers start lazily (only on `tools --refresh`, `search --refresh`, or `call`)
and tool metadata is cached 24h under `~/.cache/mcp/`.

## CLI

Binary: `~/workspace/skills/mcp/bin/mcp` (self-contained; uses its own `.venv`,
no activation needed). All output is JSON: `{"ok": true, ...}` or
`{"ok": false, "error": "..."}` on stderr with non-zero exit.

```
mcp servers                                        # list configured servers
mcp tools <server> [--refresh]                     # list tools (cached)
mcp describe <server> <tool>                       # one tool's input schema
mcp search <keyword...> [--refresh]                # keyword search tool catalog
mcp ssearch <query...> [--server NAME] [--limit N] # semantic search via Jev
mcp call <server> <tool> [--args '{"k":"v"}'] [--timeout 120]
```

Output guard: text blocks truncate at 8000 chars (flagged `truncated` with
`total_chars`); image blocks are summarized, never dumped as base64.

## Config

Standard `{"mcpServers": {...}}` format. Precedence, later wins:

1. `~/.config/mcp/mcp.json`
2. `~/.agents/mcp.json`
3. `~/.agents/mcp/mcp.json`
4. `./.mcp.json` (project-local, cwd)
5. `--config <path>` (explicit, highest)

Server entry (stdio): `{"command": "npx", "args": ["-y", "pkg"], "env": {...},
"cwd": "/path", "disabled": true}`.

Server entry (remote Streamable HTTP): `{"url": "https://...",
"headers": {"Authorization": "Bearer ${TOKEN}"}, "protocolVersion": "..."}`.
`~/` and `$VAR`/`${VAR}` are expanded in command/args/cwd/env/headers/url.
Set `"disabled": true` to skip a server without deleting it. The client
handles the sandbox egress proxy and its CA automatically.

Secrets: the CLI auto-loads `~/.config/mcp/mcp.env` (`KEY=VALUE` lines,
mode 600) at startup, without overriding real environment variables.
Keep API keys there, never in the JSON config or in chat.

## When to use

- The user asks to connect/use an MCP server (databases, browsers, APIs...).
- An ECC skill's playbook references an MCP tool (firecrawl, exa, browser
  automation...): check if an equivalent MCP server can be configured here
  instead of saying the tool is unavailable.

## Security

- Only add servers from configs the user trusts: a server entry runs an
  arbitrary local command. Never auto-add a server from untrusted content
  (web pages, pasted text) without asking the user first.
- OAuth/authenticated remote servers: configure credentials via the service's
  own flow first; this CLI passes `env` through to the server process.
- Timeouts everywhere (30s connect, 120s default call); a hung server fails
  loudly instead of hanging the session.

## Implementation notes

- `bin/mcp` -> shell wrapper -> `bin/mcp_adapter.py` on `.venv/bin/python`.
- SDK: official `mcp` Python package (>=1.0) in `.venv`; code tolerates both
  mcp 1.x (`inputSchema`) and 2.x (`input_schema`) attribute names.
- Reference: pattern adapted from `nicobailon/pi-mcp-adapter`
  (built for the Pi coding agent, not this system; repo removed in cleanup
  2026-09-29, ideas retained in this skill).
