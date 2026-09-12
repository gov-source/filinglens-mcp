# FilingLens — Python client & MCP server

**Ask any 10-K. Get the number, the sentence, and the citation.**

[FilingLens](https://filinglens.ai) answers questions about US public companies from their SEC
filings. Financial figures come straight from the company's XBRL submission (exact, with the tag
and accession number); narrative answers cite the filing section with a link to sec.gov.
Retrieval is scoped per company — no cross-company mixing.

## Install

```bash
pip install filinglens        # or: uv add filinglens
```

## MCP server (Claude Desktop · Claude Code · Cursor · any MCP client)

```json
{
  "mcpServers": {
    "filinglens": {
      "command": "uvx",
      "args": ["--from", "filinglens", "filinglens-mcp"],
      "env": { "FL_API_KEY": "fl_your_key" }
    }
  }
}
```

Claude Code: `claude mcp add filinglens -e FL_API_KEY=fl_your_key -- uvx --from filinglens filinglens-mcp`

Tools: `search_company` · `get_financials` · `list_metrics` · `index_company` · `ingest_status` · `ask_filing` · `compare_companies`

Without `FL_API_KEY` the shared demo key is used (20 questions/month). Get a free key at https://filinglens.ai.

## Python

```python
from filinglens import FilingLens

fl = FilingLens(api_key="fl_...")

fl.facts("NVDA", metrics=["revenue", "free_cash_flow", "gross_margin"], years=5)
# {'ticker': 'NVDA', 'facts': [{'metric': 'revenue', 'fiscal_year': 2026, 'display': '$215.94B',
#   'tag': 'us-gaap:Revenues', 'accn': '0001045810-26-000021', ...}, ...]}

r = fl.ask("How did data center revenue change and what drove it?", tickers=["NVDA"])
print(r["answer"])
for c in r["citations"]:
    print(c["ticker"], c["form"], c["fiscal_year"], c["section"], c["url"])

fl.compare(
    ["AAPL", "MSFT", "NVDA"],
    metrics=["revenue", "net_margin", "free_cash_flow"],
    question="Compare margin trends in the latest fiscal year.",
)
```

Async: `from filinglens import AsyncFilingLens`.

## Pricing

Free (20 questions/mo) · Pro from $15–49/mo by region · API $0.08–0.25 per question · Enterprise with
private deployment. Details: https://filinglens.ai/#pricing

## Disclaimer

FilingLens summarises and cites public SEC filings. It is not investment, legal, tax or accounting
advice. Figures are reproduced from company XBRL filings and may be restated; verify with the
original filing before relying on them.

MIT licensed. The hosted service is proprietary.
