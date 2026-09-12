"""FilingLens Python client.

    from filinglens import FilingLens
    fl = FilingLens(api_key="fl_...")
    fl.facts("AAPL", metrics=["revenue", "free_cash_flow"], years=5)
    fl.ask("What are the biggest supply-chain risks?", tickers=["AAPL"])
    fl.compare(["AAPL", "MSFT", "NVDA"], metrics=["gross_margin", "net_margin"])

Get a key at https://filinglens.ai — the free tier needs no card. Not investment advice.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

__version__ = "0.1.0"
DEFAULT_BASE_URL = "https://api.filinglens.ai"


class FilingLensError(RuntimeError):
    def __init__(self, status: int, detail: Any) -> None:
        self.status = status
        self.detail = detail
        super().__init__(f"FilingLens API {status}: {detail}")


def _raise(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise FilingLensError(resp.status_code, detail)


class _Base:
    def __init__(
        self, api_key: str | None = None, base_url: str | None = None, timeout: float = 120.0
    ) -> None:
        self.api_key = (
            api_key
            or os.environ.get("FL_API_KEY")
            or os.environ.get("FILINGLENS_API_KEY", "fl_demo")
        )
        self.base_url = (base_url or os.environ.get("FL_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._headers = {
            "X-API-Key": self.api_key,
            "User-Agent": f"filinglens-python/{__version__}",
        }


class FilingLens(_Base):
    """Synchronous client."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._c = httpx.Client(base_url=self.base_url, headers=self._headers, timeout=self.timeout)

    def _get(self, path: str, **params: Any) -> Any:
        r = self._c.get(path, params={k: v for k, v in params.items() if v is not None})
        _raise(r)
        return r.json()

    def _post(self, path: str, body: dict[str, Any]) -> Any:
        r = self._c.post(path, json=body)
        _raise(r)
        return r.json()

    def search(self, query: str) -> list[dict[str, Any]]:
        return self._get("/v1/companies/search", q=query)

    def companies(self) -> list[dict[str, Any]]:
        return self._get("/v1/companies")

    def filings(self, ticker: str) -> dict[str, Any]:
        return self._get(f"/v1/companies/{ticker}/filings")

    def facts(
        self, ticker: str, metrics: list[str] | None = None, years: int = 5, period: str = "FY"
    ) -> dict[str, Any]:
        return self._get(
            f"/v1/companies/{ticker}/facts",
            metrics=",".join(metrics) if metrics else None,
            years=years,
            period=period,
        )

    def ingest(self, ticker: str, forms: list[str] | None = None, limit: int = 1) -> dict[str, Any]:
        return self._post(
            f"/v1/companies/{ticker}/ingest", {"forms": forms or ["10-K"], "limit": limit}
        )

    def ingest_status(self, job_id: str) -> dict[str, Any]:
        return self._get(f"/v1/ingest/{job_id}")

    def ask(
        self,
        question: str,
        tickers: list[str],
        fiscal_years: list[int] | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        return self._post(
            "/v1/ask",
            {
                "question": question,
                "tickers": tickers,
                "fiscal_years": fiscal_years,
                "history": history,
            },
        )

    def compare(
        self,
        tickers: list[str],
        metrics: list[str] | None = None,
        question: str | None = None,
        years: int = 3,
    ) -> dict[str, Any]:
        return self._post(
            "/v1/compare",
            {"tickers": tickers, "metrics": metrics, "question": question, "years": years},
        )

    def usage(self) -> dict[str, Any]:
        return self._get("/v1/usage")

    def metrics(self) -> list[dict[str, str]]:
        return self._get("/v1/metrics")

    def feedback(self, usage_id: int | None, score: int, note: str | None = None) -> dict[str, Any]:
        return self._post("/v1/feedback", {"usage_id": usage_id, "score": score, "note": note})


class AsyncFilingLens(_Base):
    """Async client (same methods as FilingLens, awaitable)."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._c = httpx.AsyncClient(
            base_url=self.base_url, headers=self._headers, timeout=self.timeout
        )

    async def _get(self, path: str, **params: Any) -> Any:
        r = await self._c.get(path, params={k: v for k, v in params.items() if v is not None})
        _raise(r)
        return r.json()

    async def _post(self, path: str, body: dict[str, Any]) -> Any:
        r = await self._c.post(path, json=body)
        _raise(r)
        return r.json()

    async def search(self, query: str) -> list[dict[str, Any]]:
        return await self._get("/v1/companies/search", q=query)

    async def companies(self) -> list[dict[str, Any]]:
        return await self._get("/v1/companies")

    async def facts(
        self, ticker: str, metrics: list[str] | None = None, years: int = 5, period: str = "FY"
    ) -> dict[str, Any]:
        return await self._get(
            f"/v1/companies/{ticker}/facts",
            metrics=",".join(metrics) if metrics else None,
            years=years,
            period=period,
        )

    async def ingest(
        self, ticker: str, forms: list[str] | None = None, limit: int = 1
    ) -> dict[str, Any]:
        return await self._post(
            f"/v1/companies/{ticker}/ingest", {"forms": forms or ["10-K"], "limit": limit}
        )

    async def ingest_status(self, job_id: str) -> dict[str, Any]:
        return await self._get(f"/v1/ingest/{job_id}")

    async def ask(
        self,
        question: str,
        tickers: list[str],
        fiscal_years: list[int] | None = None,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        return await self._post(
            "/v1/ask",
            {
                "question": question,
                "tickers": tickers,
                "fiscal_years": fiscal_years,
                "history": history,
            },
        )

    async def compare(
        self,
        tickers: list[str],
        metrics: list[str] | None = None,
        question: str | None = None,
        years: int = 3,
    ) -> dict[str, Any]:
        return await self._post(
            "/v1/compare",
            {"tickers": tickers, "metrics": metrics, "question": question, "years": years},
        )

    async def usage(self) -> dict[str, Any]:
        return await self._get("/v1/usage")

    async def metrics(self) -> list[dict[str, str]]:
        return await self._get("/v1/metrics")

    async def aclose(self) -> None:
        await self._c.aclose()


__all__ = ["AsyncFilingLens", "FilingLens", "FilingLensError", "__version__"]
