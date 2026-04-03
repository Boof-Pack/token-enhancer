# Changelog

## 0.2.0 — 2026-04-03

### Fixed

- **Installed missing dependencies** — `flask`, `beautifulsoup4`, and `mcp` were absent from the venv despite being listed in `requirements.txt`. Nothing worked without this.

- **Fixed relative `DB_PATH`** — `data_proxy.py` and `proxy.py` both used `"agent_proxy.db"` as a bare filename. When the MCP server is spawned by Claude Desktop the working directory is unpredictable, so the database was created in the wrong location. Changed to `Path(__file__).parent / "agent_proxy.db"` in both files.

- **Errors now raise instead of return** — `fetch_clean` and `fetch_clean_batch` were returning error strings on failure. FastMCP sends these as successful tool responses (`isError: false`), so the client saw errors as content. Changed to `raise RuntimeError(...)` so FastMCP correctly sets `isError: true`.

- **Batch size limit enforced in MCP tool** — `fetch_clean_batch` had no URL count cap. The HTTP proxy enforced a 10-URL limit via `validate_batch`, but the MCP tool bypassed it. Added `validate_batch(urls)` call to the MCP tool.

- **`init_data_db()` moved inside `mcp.run()`** — Database initialisation ran at module import time, before the MCP handshake. A sqlite failure would crash the server before any tools were registered. Moved inside `if __name__ == "__main__"` with a `try/except` that logs a warning and continues on failure.

- **Blocking `requests.get` wrapped with `anyio.to_thread.run_sync`** — FastMCP runs on an async event loop but calls sync tools directly, blocking the loop. A 30-second `requests.get` timeout on a slow URL would make Claude Desktop treat the server as hung. All three tools are now `async` and dispatch blocking calls to a thread via `anyio.to_thread.run_sync(functools.partial(...))`.

### Added

- **Startup dependency check** — `mcp_server.py` now checks for `mcp`, `flask`, and `bs4` at import time using `importlib.util.find_spec`. Missing packages print a clear message with the exact install command and exit with code 1 before the MCP handshake starts.

- **GitHub benchmark in README** — Added measured result: GitHub repo page, 171,234 raw tokens → 6,976 cleaned, 95.9% reduction.

- **MCP Registry publication** — `server.json` schema updated to `2025-12-11`, `title` field added, `identifier` corrected to match the PyPI package name. Server published to `registry.modelcontextprotocol.io` as `io.github.xelektron/token-enhancer`.
