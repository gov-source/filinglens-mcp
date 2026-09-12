"""FilingLens MCP server (remote): exposes the hosted FilingLens API as MCP tools.

Claude Desktop / Claude Code / Cursor config:
    {"mcpServers": {"filinglens": {"command": "filinglens-mcp", "env": {"FL_API_KEY": "fl_..."}}}}
Or with uvx (no install):  {"command": "uvx", "args": ["--from", "filinglens", "filinglens-mcp"]}

Without FL_API_KEY the free demo key is used (20 questions/month, shared).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from typing import Any

from mcp.server.mcpserver import MCPServer

from . import AsyncFilingLens, FilingLensError, __version__

mcp = MCPServer(
    "FilingLens",
    version=__version__,
    instructions=(
        "Answer questions about US public companies from their SEC filings via FilingLens. "
        "get_financials returns exact XBRL figures; ask_filing returns cited narrative answers. "
        "Call index_company for a ticker not yet indexed (check the error hint). "
        "Present figures with fiscal year and source; never as investment advice."
    ),
)
_client: AsyncFilingLens | None = None
logging.getLogger("httpx").setLevel(logging.WARNING)  # keep stdio transport clean


def _c() -> AsyncFilingLens:
    global _client
    if _client is None:
        _client = AsyncFilingLens()
    return _client


def _safe(coro: Any) -> Any:
    async def run() -> Any:
        try:
            return await coro
        except FilingLensError as e:
            return {"error": e.detail, "status": e.status}

    return run()


@mcp.tool()
async def search_company(query: str) -> Any:
    """Find a US-listed company's ticker and CIK by name or ticker fragment."""
    return await _safe(_c().search(query))


@mcp.tool()
async def get_financials(ticker: str, metrics: list[str] | None = None, years: int = 5) -> Any:
    """Exact fiscal-year financials from the company's XBRL filings (revenue, net_income, operating_income,
    gross_profit, total_assets, total_liabilities, stockholders_equity, cash, operating_cash_flow, capex,
    free_cash_flow, rnd, sga, eps_diluted, long_term_debt, buybacks, dividends_paid, gross_margin,
    operating_margin, net_margin, ...). Each value carries its XBRL tag and filing accession number."""
    return await _safe(_c().facts(ticker, metrics=metrics, years=years))


@mcp.tool()
async def list_metrics() -> Any:
    """List every metric key get_financials understands."""
    return await _safe(_c().metrics())


@mcp.tool()
async def index_company(ticker: str, forms: list[str] | None = None, limit: int = 1) -> Any:
    """Index the latest filings (default: most recent 10-K) for a ticker so ask_filing can use it.
    Returns a job id; indexing takes ~20–60 seconds. Poll with ingest_status."""
    return await _safe(_c().ingest(ticker, forms=forms, limit=limit))


@mcp.tool()
async def ingest_status(job_id: str) -> Any:
    """Check an index_company job."""
    return await _safe(_c().ingest_status(job_id))


@mcp.tool()
async def ask_filing(
    question: str, tickers: list[str], fiscal_years: list[int] | None = None
) -> Any:
    """Answer a question from one or more companies' SEC filings with citations (section, form,
    fiscal year, sec.gov URL). Figures come from XBRL. Requires the ticker to be indexed."""
    return await _safe(_c().ask(question, tickers, fiscal_years=fiscal_years))


@mcp.tool()
async def compare_companies(
    tickers: list[str], metrics: list[str] | None = None, question: str | None = None
) -> Any:
    """Side-by-side XBRL comparison of 2–10 companies, optionally with a cited narrative answer."""
    return await _safe(_c().compare(tickers, metrics=metrics, question=question))


def main() -> None:
    p = argparse.ArgumentParser(description="FilingLens MCP server")
    p.add_argument(
        "--http", action="store_true", help="serve over streamable HTTP instead of stdio"
    )
    p.add_argument("--port", type=int, default=8765)
    a = p.parse_args()
    try:
        if a.http:
            mcp.run(transport="streamable-http", host="0.0.0.0", port=a.port)
        else:
            mcp.run(transport="stdio")
    finally:
        if _client is not None:
            asyncio.run(_client.aclose())


if __name__ == "__main__":
    main()
