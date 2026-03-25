"""
Token Enhancer MCP Server
Exposes fetch_clean and refine_prompt as MCP tools.
Works with Claude Desktop, Cursor, OpenClaw, and any MCP client.

Install:
    pip install mcp

Run:
    python mcp_server.py

Add to Claude Desktop config (~/Library/Application Support/Claude/claude_desktop_config.json on Mac):
    {
      "mcpServers": {
        "token-enhancer": {
          "command": "python",
          "args": ["/FULL/PATH/TO/mcp_server.py"]
        }
      }
    }
"""

from mcp.server.fastmcp import FastMCP
from data_proxy import fetch_and_clean, init_data_db
from optimizer import optimize_prompt

# Initialize
init_data_db()
mcp = FastMCP("token-enhancer")


@mcp.tool()
def fetch_clean(url: str, ttl: int = 300) -> str:
    """Fetch a URL and return clean text with all HTML noise removed.
    Strips navigation, ads, scripts, styles, and boilerplate.
    Caches results to avoid redundant fetches.
    Typical reduction: 86-99% fewer tokens than raw HTML.

    Args:
        url: The URL to fetch and clean
        ttl: Cache duration in seconds (default 300)
    """
    result = fetch_and_clean(url, ttl)

    if result.error:
        return f"Error fetching {url}: {result.error}"

    reduction = 0
    if result.original_tokens > 0:
        reduction = round((1 - result.cleaned_tokens / result.original_tokens) * 100, 1)

    header = (
        f"[Token Enhancer] {result.original_tokens:,} -> {result.cleaned_tokens:,} tokens "
        f"({reduction}% reduced)"
    )
    if result.from_cache:
        header += " [cached]"

    return f"{header}\n\n{result.content}"


@mcp.tool()
def fetch_clean_batch(urls: list[str], ttl: int = 300) -> str:
    """Fetch multiple URLs and return clean text for each.
    Each URL is stripped of HTML noise and cached independently.

    Args:
        urls: List of URLs to fetch and clean
        ttl: Cache duration in seconds (default 300)
    """
    results = []
    total_original = 0
    total_cleaned = 0

    for url in urls:
        r = fetch_and_clean(url, ttl)
        total_original += r.original_tokens
        total_cleaned += r.cleaned_tokens

        if r.error:
            results.append(f"--- {url} ---\nError: {r.error}\n")
        else:
            results.append(f"--- {url} ---\n{r.content}\n")

    reduction = 0
    if total_original > 0:
        reduction = round((1 - total_cleaned / total_original) * 100, 1)

    header = (
        f"[Token Enhancer] {len(urls)} URLs | "
        f"{total_original:,} -> {total_cleaned:,} tokens ({reduction}% reduced)\n\n"
    )

    return header + "\n".join(results)


@mcp.tool()
def refine_prompt(text: str) -> str:
    """Refine a prompt by removing filler words while preserving
    entities, negations, time references, and conversation context.
    Returns both the original and suggested version so you can choose.

    Args:
        text: The prompt text to refine
    """
    result = optimize_prompt(text)

    savings = 0
    if result.original_tokens > 0:
        savings = round((1 - result.optimized_tokens / result.original_tokens) * 100, 1)

    output = f"Original ({result.original_tokens} tokens):\n{result.original}\n\n"

    if result.sent_optimized:
        output += f"Suggested ({result.optimized_tokens} tokens, {savings}% smaller):\n{result.optimized}\n\n"
        output += f"Protected: {', '.join(result.protected_entities[:8])}\n"
        output += f"Confidence: {result.confidence:.0%}"
    else:
        output += f"No optimization needed. Reason: {result.skip_reason}"

    return output


if __name__ == "__main__":
    mcp.run()
