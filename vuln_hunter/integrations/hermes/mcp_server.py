"""MCP server for Hermes Agent."""
def start_server(transport="stdio", port=8000):
    from fastmcp import FastMCP
    mcp = FastMCP("vulnhunter-ai", version="1.0.0")
    @mcp.tool()
    async def scan_start(target: str, intensity: str = "normal") -> str:
        return f"Started: {target}"
    @mcp.tool()
    async def scan_findings(id: str = "") -> str: return "[]"
    @mcp.tool()
    async def scan_report(id: str = "", fmt: str = "markdown") -> str: return f"Report ({fmt})"
    @mcp.tool()
    async def scan_status(id: str = "") -> str: return "running"
    @mcp.tool()
    async def vuln_explainer(v: str) -> str: return f"Explained: {v}"
    @mcp.tool()
    async def tool_runner(tool: str, target: str) -> str: return f"{tool} -> {target}"
    @mcp.tool()
    async def tool_list(cat: str = "") -> str: return "nmap,nuclei,sqlmap"
    if transport == "sse": mcp.run(transport="sse", port=port)
    else: mcp.run(transport="stdio")
