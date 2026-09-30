#!/usr/bin/env python3
"""mcp - token-efficient MCP adapter CLI for Pi (Muse).

Inspired by nicobailon/pi-mcp-adapter, rebuilt for this system:
- one small CLI instead of hundreds of tool definitions in context
- servers start lazily, only when actually used
- tool metadata is cached on disk; search/describe work without live connections
- output guard: long text truncated, images summarized (no base64 dumps)

Config (standard {"mcpServers": {...}} format, later wins):
  1. ~/.config/mcp/mcp.json
  2. ~/.agents/mcp.json
  3. ~/.agents/mcp/mcp.json
  4. ./.mcp.json            (project-local, highest precedence)
  --config <path> adds one more file on top.
  A server entry may set "disabled": true to skip it.

Usage:
  mcp servers
  mcp tools <server> [--refresh]
  mcp describe <server> <tool>
  mcp search <keywords...> [--refresh]
  mcp ssearch <query...> [--server NAME] [--limit N] [--min-prob 0.25]
                         [--model MODEL] [--no-cache]
  mcp call <server> <tool> [--args '{"k":"v"}'] [--timeout 120]
"""

import argparse
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CONFIG_PATHS = [
    Path.home() / ".config" / "mcp" / "mcp.json",
    Path.home() / ".agents" / "mcp.json",
    Path.home() / ".agents" / "mcp" / "mcp.json",
]
PROJECT_CONFIG = Path.cwd() / ".mcp.json"
CACHE_DIR = Path.home() / ".cache" / "mcp" / "tools"
CACHE_TTL = 24 * 3600
TEXT_LIMIT = 8000
CONNECT_TIMEOUT = 30

# semantic search (Jev-backed, pi-mcp-adapter pattern)
# Send (nearly) all tools to Jev in one call: lexical pre-filtering cannot work
# for cross-lingual queries (e.g. Vietnamese query vs English tool names), so a
# fixed small budget would silently drop the right tool. Judge choice supports
# up to 255 options; per-question cache makes repeat queries free.
SSEARCH_CANDIDATE_LIMIT = 150  # hard cap; pre-filter only kicks in beyond this
SSEARCH_DESC_TRUNC = 200       # chars of description per candidate
SSEARCH_MIN_PROB = 0.25        # below this top probability -> abstain
JUDGE_BIN = os.environ.get("JUDGE_BIN") or str(
    Path(__file__).resolve().parent.parent.parent / "judge" / "bin" / "judge")


def _load_dotenv():
    """Load ~/.config/mcp/mcp.env (KEY=VALUE lines) without overriding real env."""
    p = Path.home() / ".config" / "mcp" / "mcp.env"
    try:
        text = p.read_text()
    except Exception:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip("'\"")
        if k and k not in os.environ:
            os.environ[k] = v


_load_dotenv()


def fail(msg, code=1):
    print(json.dumps({"ok": False, "error": msg}), file=sys.stderr)
    sys.exit(code)


def expand(s):
    if not isinstance(s, str):
        return s
    s = os.path.expanduser(s)
    return os.path.expandvars(s)


def load_servers(extra_config=None):
    servers = {}
    sources = list(CONFIG_PATHS)
    if extra_config:
        sources.append(Path(extra_config))
    sources.append(PROJECT_CONFIG)
    for p in sources:
        try:
            data = json.loads(Path(p).read_text())
        except Exception:
            continue
        for name, cfg in (data.get("mcpServers") or {}).items():
            if isinstance(cfg, dict):
                servers[name] = cfg
    return servers


def get_server(servers, name):
    cfg = servers.get(name)
    if cfg is None:
        fail(f"unknown server: {name}")
    if cfg.get("disabled"):
        fail(f"server disabled: {name}")
    if not cfg.get("command") and not cfg.get("url"):
        fail(f"server '{name}' has no command or url")
    return cfg


def cache_file(name):
    digest = hashlib.sha256(name.encode()).hexdigest()[:16]
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)[:40]
    return CACHE_DIR / f"{safe}-{digest}.json"


def config_hash(cfg):
    return hashlib.sha256(
        json.dumps(cfg, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]


def read_cache(name, cfg):
    p = cache_file(name)
    try:
        data = json.loads(p.read_text())
    except Exception:
        return None
    if data.get("config_hash") != config_hash(cfg):
        return None
    if time.time() - data.get("fetched_at", 0) > CACHE_TTL:
        return None
    return data.get("tools")


def write_cache(name, cfg, tools):
    p = cache_file(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "config_hash": config_hash(cfg),
        "fetched_at": time.time(),
        "tools": tools,
    }))


# ---------- MCP session ----------

from contextlib import asynccontextmanager


@asynccontextmanager
async def _transport(cfg):
    """Yield (read, write) streams for a stdio or remote-HTTP MCP server."""
    if cfg.get("url"):
        from mcp.client.streamable_http import streamable_http_client
        import httpx

        headers = {k: expand(v) for k, v in (cfg.get("headers") or {}).items()}
        if cfg.get("protocolVersion"):
            headers.setdefault("MCP-Protocol-Version", cfg["protocolVersion"])
        # trust_env=False: httpx chokes on some no_proxy entries (e.g. IPv6
        # literals like [::1]); pass the egress proxy explicitly instead.
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        ca = os.environ.get("SSL_CERT_FILE") or "/run/hatch/egress-tls/ca-bundle.pem"
        verify = ca if ca and os.path.exists(ca) else True
        client = httpx.AsyncClient(headers=headers, timeout=CONNECT_TIMEOUT,
                                   proxy=proxy or None, trust_env=False,
                                   verify=verify)
        async with streamable_http_client(expand(cfg["url"]),
                                          http_client=client) as streams:
            yield streams
    else:
        from mcp import StdioServerParameters
        from mcp.client.stdio import stdio_client

        params = StdioServerParameters(
            command=expand(cfg["command"]),
            args=[expand(a) for a in cfg.get("args", [])],
            env={**os.environ,
                 **{k: expand(v) for k, v in (cfg.get("env") or {}).items()}},
            cwd=expand(cfg["cwd"]) if cfg.get("cwd") else None,
        )
        async with stdio_client(params) as streams:
            yield streams


def _caused_by_unsupported_version(exc):
    """Walk an exception tree (incl. anyio ExceptionGroups) looking for the
    SDK's 'Unsupported protocol version' RuntimeError."""
    seen, stack = set(), [exc]
    while stack:
        e = stack.pop()
        if id(e) in seen:
            continue
        seen.add(id(e))
        if isinstance(e, RuntimeError) and "Unsupported protocol version" in str(e):
            return True
        if isinstance(e, BaseExceptionGroup):
            stack.extend(e.exceptions)
        if e.__cause__ is not None:
            stack.append(e.__cause__)
        if e.__context__ is not None and e.__context__ is not e.__cause__:
            stack.append(e.__context__)
    return False


async def _fetch_tools(cfg):
    from mcp import ClientSession

    try:
        async with _transport(cfg) as (read, write):
            async with ClientSession(read, write) as session:
                await asyncio.wait_for(session.initialize(), timeout=CONNECT_TIMEOUT)
                result = await asyncio.wait_for(session.list_tools(), timeout=CONNECT_TIMEOUT)
                return [
                    {
                        "name": t.name,
                        "description": t.description or "",
                        # mcp 1.x: inputSchema, mcp 2.x: input_schema
                        "inputSchema": getattr(t, "inputSchema", None)
                        or getattr(t, "input_schema", None)
                        or {"type": "object"},
                    }
                    for t in result.tools
                ]
    except BaseException as e:
        # SDK 2.x legacy session only handshakes 2024-11-05..2025-11-25.
        # Some servers (e.g. Eta ETAPI) hardcode protocolVersion 2026-07-28
        # and speak plain stateless JSON-RPC over HTTP — talk to them directly.
        if not _caused_by_unsupported_version(e):
            raise
        return await _raw_fetch_tools(cfg)


async def _call_tool(cfg, tool, args, timeout):
    from mcp import ClientSession

    try:
        async with _transport(cfg) as (read, write):
            async with ClientSession(read, write) as session:
                await asyncio.wait_for(session.initialize(), timeout=CONNECT_TIMEOUT)
                return await asyncio.wait_for(
                    session.call_tool(tool, args), timeout=timeout
                )
    except BaseException as e:
        if not _caused_by_unsupported_version(e):
            raise
        return await _raw_call_tool(cfg, tool, args, timeout)


# ---------- raw JSON-RPC fallback (stateless Streamable HTTP servers) ----------

from types import SimpleNamespace as _SimpleNamespace


def _raw_http_client(cfg):
    import httpx

    headers = {k: expand(v) for k, v in (cfg.get("headers") or {}).items()}
    if cfg.get("protocolVersion"):
        headers.setdefault("MCP-Protocol-Version", cfg["protocolVersion"])
    headers.setdefault("Accept", "application/json, text/event-stream")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    ca = os.environ.get("SSL_CERT_FILE") or "/run/hatch/egress-tls/ca-bundle.pem"
    verify = ca if ca and os.path.exists(ca) else True
    return httpx.AsyncClient(headers=headers, timeout=CONNECT_TIMEOUT,
                             proxy=proxy or None, trust_env=False, verify=verify)


async def _raw_rpc(client, url, method, params=None, req_id=None, timeout=CONNECT_TIMEOUT):
    body = {"jsonrpc": "2.0", "method": method}
    if req_id is not None:
        body["id"] = req_id
    if params is not None:
        body["params"] = params
    r = await client.post(url, json=body, timeout=timeout)
    r.raise_for_status()
    if not r.content:
        return None
    data = r.json()
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return (data or {}).get("result")


async def _raw_handshake(client, url):
    await _raw_rpc(client, url, "initialize", {
        "protocolVersion": "2026-07-28",
        "capabilities": {},
        "clientInfo": {"name": "pi-mcp", "version": "1.0"},
    }, req_id=1)
    # notification: fire and forget (202 with empty body is fine)
    try:
        await _raw_rpc(client, url, "notifications/initialized")
    except Exception:
        pass


async def _raw_fetch_tools(cfg):
    url = expand(cfg["url"])
    client = _raw_http_client(cfg)
    async with client:
        await _raw_handshake(client, url)
        result = await _raw_rpc(client, url, "tools/list", {}, req_id=2) or {}
        return [
            {
                "name": t.get("name", ""),
                "description": t.get("description") or "",
                "inputSchema": t.get("inputSchema") or t.get("input_schema")
                or {"type": "object"},
            }
            for t in result.get("tools", [])
        ]


def _raw_block(b):
    t = (b or {}).get("type", "unknown")
    return _SimpleNamespace(
        type=t,
        text=(b or {}).get("text", ""),
        data=(b or {}).get("data", ""),
        mimeType=(b or {}).get("mimeType") or (b or {}).get("mime_type", ""),
    )


async def _raw_call_tool(cfg, tool, args, timeout):
    url = expand(cfg["url"])
    client = _raw_http_client(cfg)
    async with client:
        await _raw_handshake(client, url)
        result = await _raw_rpc(
            client, url, "tools/call",
            {"name": tool, "arguments": args or {}},
            req_id=3, timeout=timeout,
        ) or {}
        return _SimpleNamespace(
            isError=bool(result.get("isError", False)),
            content=[_raw_block(b) for b in result.get("content", [])],
        )


def fetch_tools(cfg):
    try:
        return asyncio.run(_fetch_tools(cfg))
    except Exception as e:
        fail(f"failed to connect/list tools: {e}", code=2)


def call_tool(cfg, tool, args, timeout):
    try:
        return asyncio.run(_call_tool(cfg, tool, args, timeout))
    except Exception as e:
        fail(f"tool call failed: {e}", code=2)


def get_tools(name, cfg, refresh=False):
    if not refresh:
        cached = read_cache(name, cfg)
        if cached is not None:
            return cached, True
    tools = fetch_tools(cfg)
    write_cache(name, cfg, tools)
    return tools, False


# ---------- output rendering ----------

def render_result(result):
    out = {"isError": bool(getattr(result, "isError", getattr(result, "is_error", False))),
           "content": []}
    for b in result.content or []:
        btype = getattr(b, "type", "unknown")
        if btype == "text":
            text = b.text or ""
            if len(text) > TEXT_LIMIT:
                out["content"].append({
                    "type": "text",
                    "text": text[:TEXT_LIMIT],
                    "truncated": True,
                    "total_chars": len(text),
                })
            else:
                out["content"].append({"type": "text", "text": text})
        elif btype == "image":
            data = getattr(b, "data", "") or ""
            out["content"].append({
                "type": "image",
                "mimeType": getattr(b, "mimeType", getattr(b, "mime_type", "")),
                "approx_bytes": len(data) * 3 // 4,
                "note": "image content withheld; re-run with a screenshot-capable viewer if needed",
            })
        elif btype == "resource":
            r = b.resource
            out["content"].append({
                "type": "resource",
                "uri": str(getattr(r, "uri", "")),
                "mimeType": getattr(r, "mimeType", ""),
            })
        else:
            out["content"].append({"type": btype, "note": "unrendered block"})
    return out


# ---------- commands ----------

def cmd_servers(servers):
    rows = []
    for name in sorted(servers):
        cfg = servers[name]
        cached = read_cache(name, cfg)
        rows.append({
            "name": name,
            "transport": "http" if cfg.get("url") else "stdio",
            "target": cfg.get("url") or cfg.get("command"),
            "disabled": bool(cfg.get("disabled")),
            "cached_tools": len(cached) if cached is not None else 0,
        })
    print(json.dumps({"ok": True, "servers": rows}, indent=2))


def cmd_tools(servers, name, refresh):
    cfg = get_server(servers, name)
    tools, from_cache = get_tools(name, cfg, refresh)
    print(json.dumps({
        "ok": True,
        "server": name,
        "from_cache": from_cache,
        "tools": [
            {"name": t["name"], "description": t["description"]} for t in tools
        ],
    }, indent=2))


def cmd_describe(servers, name, tool):
    cfg = get_server(servers, name)
    tools, _ = get_tools(name, cfg)
    for t in tools:
        if t["name"] == tool:
            print(json.dumps({"ok": True, "server": name, "tool": t}, indent=2))
            return
    fail(f"tool not found on {name}: {tool}")


def cmd_search(servers, keywords, refresh):
    kws = [k.lower() for k in keywords]
    hits = []
    errors = []
    for name in sorted(servers):
        cfg = servers[name]
        if cfg.get("disabled"):
            continue
        try:
            tools, _ = get_tools(name, cfg, refresh)
        except SystemExit:
            errors.append(name)
            continue
        for t in tools:
            hay_name = t["name"].lower()
            hay_desc = (t["description"] or "").lower()
            score = 0
            for k in kws:
                if k in hay_name:
                    score += 3
                elif k in hay_desc:
                    score += 1
            if score:
                hits.append({
                    "server": name,
                    "tool": t["name"],
                    "description": t["description"],
                    "score": score,
                })
    hits.sort(key=lambda h: -h["score"])
    print(json.dumps({"ok": True, "hits": hits[:30], "errors": errors}, indent=2))


def _all_pairs(servers, only_server=None):
    """[(server, tool_dict)] across servers, skipping disabled/errored ones."""
    pairs, errors = [], []
    for name in sorted(servers):
        if only_server and name != only_server:
            continue
        cfg = servers[name]
        if cfg.get("disabled"):
            continue
        try:
            tools, _ = get_tools(name, cfg, False)
        except SystemExit:
            errors.append(name)
            continue
        pairs.extend((name, t) for t in tools)
    return pairs, errors


def _score_pairs(pairs, words):
    """Lexical score list of (score, server, tool), best first."""
    scored = []
    for server, t in pairs:
        hay_name = t["name"].lower()
        hay_desc = (t["description"] or "").lower()
        score = 0
        for k in words:
            if k in hay_name:
                score += 3
            elif k in hay_desc:
                score += 1
        scored.append((score, server, t))
    scored.sort(key=lambda x: -x[0])
    return scored


def _select_candidates(pairs, query):
    """Cap candidates: top lexical half + round-robin across servers for breadth."""
    if len(pairs) <= SSEARCH_CANDIDATE_LIMIT:
        return list(pairs)
    words = query.lower().split()
    scored = _score_pairs(pairs, words)
    half = SSEARCH_CANDIDATE_LIMIT // 2
    top = [(s, t) for _, s, t in scored[:half]]
    picked = {(s, t["name"]) for s, t in top}
    rest = [(s, t) for _, s, t in scored[half:] if (s, t["name"]) not in picked]
    by_server = {}
    for s, t in rest:
        by_server.setdefault(s, []).append((s, t))
    servers_sorted = sorted(by_server)
    rr, i = [], 0
    budget = SSEARCH_CANDIDATE_LIMIT - len(top)
    while len(rr) < budget:
        added = False
        for srv in servers_sorted:
            if len(rr) >= budget:
                break
            if i < len(by_server[srv]):
                rr.append(by_server[srv][i])
                added = True
        if not added:
            break
        i += 1
    return top + rr


def _judge_choice(query, candidates, model=None, no_cache=False):
    """Ask Jev (via the judge skill CLI) which candidate best matches the query."""
    criteria = {}
    cand_list = []
    for i, (server, t) in enumerate(candidates):
        cid = f"c{i}"
        desc = (t.get("description") or "")[:SSEARCH_DESC_TRUNC]
        cand_list.append({"id": cid, "server": server,
                          "tool": t["name"], "description": desc})
        criteria[cid] = f"{server}.{t['name']}"
    criteria["none"] = "No tool is suitable for this query"
    req = {
        "state": {"query": query, "candidates": cand_list},
        "questions": {
            "match": {
                "type": "choice",
                "instructions": ("Rank which tool best matches the user's query. "
                                 "Choose none when no tool is suitable."),
                "criteria": criteria,
            }
        },
    }
    if model:
        req["model"] = model
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(req, f, ensure_ascii=False)
        path = f.name
    try:
        proc = subprocess.run(
            [JUDGE_BIN, "--file", path] + (["--no-cache"] if no_cache else []),
            capture_output=True, text=True, timeout=180)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "judge failed").strip()[:300]
        raise RuntimeError(f"judge error: {err}")
    try:
        out = json.loads(proc.stdout)
        ans = out["answers"]["match"]
    except Exception as e:
        raise RuntimeError(f"bad judge response: {e}")
    if not isinstance(ans, dict) or ans.get("type") != "choice":
        raise RuntimeError("judge did not return a choice answer")
    return out, ans, cand_list


def cmd_ssearch(servers, query_words, only_server=None, limit=10,
                min_prob=SSEARCH_MIN_PROB, model=None, no_cache=False):
    query = " ".join(query_words).strip()
    if not query:
        fail("empty query")
    pairs, errors = _all_pairs(servers, only_server)
    if not pairs:
        fail("no tools available" + (f" (errors: {errors})" if errors else ""))
    candidates = _select_candidates(pairs, query)

    def lexical_fallback(reason):
        words = query.lower().split()
        hits = [{"server": s, "tool": t["name"],
                 "description": t.get("description") or "", "score": sc}
                for sc, s, t in _score_pairs(candidates, words)[:limit] if sc > 0]
        print(json.dumps({"ok": True, "query": query, "backend": "lexical-fallback",
                          "degraded": True, "reason": reason,
                          "abstained": not hits, "matches": hits,
                          "errors": errors}, indent=2, ensure_ascii=False))

    try:
        out, ans, cand_list = _judge_choice(query, candidates, model, no_cache)
    except Exception as e:
        lexical_fallback(str(e))
        return

    probs = ans.get("probabilities") or {}
    ranked = sorted(((probs.get(c["id"], 0.0), c) for c in cand_list),
                    key=lambda x: -x[0])
    top_prob = ranked[0][0] if ranked else 0.0
    none_prob = probs.get("none", 0.0)
    abstained = (ans.get("choice") == "none" or none_prob >= top_prob
                 or top_prob < min_prob)
    matches = [] if abstained else [
        {"server": c["server"], "tool": c["tool"],
         "description": c["description"], "probability": round(p, 4)}
        for p, c in ranked[:limit] if p > 0
    ]
    print(json.dumps({
        "ok": True, "query": query, "backend": "semantic", "degraded": False,
        "model": out.get("model"), "usage": out.get("usage"),
        "cached": out.get("cached", []),
        "abstained": abstained,
        "matches": matches, "errors": errors,
    }, indent=2, ensure_ascii=False))


def cmd_call(servers, name, tool, args_s, timeout):
    cfg = get_server(servers, name)
    try:
        args = json.loads(args_s) if args_s else {}
    except Exception as e:
        fail(f"bad --args JSON: {e}")
    if not isinstance(args, dict):
        fail("--args must be a JSON object")
    result = call_tool(cfg, tool, args, timeout)
    print(json.dumps({"ok": True, "server": name, "tool": tool,
                      "result": render_result(result)}, indent=2))


def main():
    ap = argparse.ArgumentParser(prog="mcp", description="token-efficient MCP adapter CLI")
    ap.add_argument("--config", help="extra MCP config file (highest precedence)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("servers", help="list configured servers")

    p = sub.add_parser("tools", help="list a server's tools (cached)")
    p.add_argument("server")
    p.add_argument("--refresh", action="store_true")

    p = sub.add_parser("describe", help="show one tool's input schema")
    p.add_argument("server")
    p.add_argument("tool")

    p = sub.add_parser("search", help="keyword search over cached tool metadata")
    p.add_argument("keywords", nargs="+")
    p.add_argument("--refresh", action="store_true")

    p = sub.add_parser("ssearch", help="semantic tool search via Jev (falls back to keyword)")
    p.add_argument("query", nargs="+", help="natural-language request, e.g. 'xem don hang hom nay'")
    p.add_argument("--server", default=None, help="restrict to one server")
    p.add_argument("--limit", type=int, default=10, help="max matches to show")
    p.add_argument("--min-prob", type=float, default=SSEARCH_MIN_PROB,
                   help="abstain when top probability is below this")
    p.add_argument("--model", default=None, help="override Jev model")
    p.add_argument("--no-cache", action="store_true", help="bypass judge answer cache")

    p = sub.add_parser("call", help="call a tool")
    p.add_argument("server")
    p.add_argument("tool")
    p.add_argument("--args", default="", help='JSON object, e.g. \'{"path": "/tmp"}\'')
    p.add_argument("--timeout", type=int, default=120)

    ns = ap.parse_args()
    servers = load_servers(ns.config)
    if ns.cmd == "servers":
        cmd_servers(servers)
    elif ns.cmd == "tools":
        cmd_tools(servers, ns.server, ns.refresh)
    elif ns.cmd == "describe":
        cmd_describe(servers, ns.server, ns.tool)
    elif ns.cmd == "search":
        cmd_search(servers, ns.keywords, ns.refresh)
    elif ns.cmd == "ssearch":
        cmd_ssearch(servers, ns.query, ns.server, ns.limit,
                    ns.min_prob, ns.model, ns.no_cache)
    elif ns.cmd == "call":
        cmd_call(servers, ns.server, ns.tool, ns.args, ns.timeout)


if __name__ == "__main__":
    main()
