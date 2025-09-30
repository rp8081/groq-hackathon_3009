import datetime
import random
from typing import Dict, Any, List

import pandas as pd
from langchain_core.messages import AIMessage

# Try MCP client import
try:
    from langchain_mcp import ClientSession
except ImportError:
    ClientSession = None

import yfinance as yf


class MarketDataAgent:
    name = "MarketDataAgent"

    def __init__(self, llm=None):
        self.llm = llm

    async def _fetch_from_mcp(self, tickers: List[str]) -> Dict[str, List[float]]:
        """Call MCP get_prices tool for latest prices."""
        import os

        endpoint = os.environ.get("MCP_MARKET_ENDPOINT")
        if not endpoint or ClientSession is None:
            return {}

        async with ClientSession(endpoint=endpoint) as session:
            result = await session.call_tool("get_prices", {"tickers": tickers})
            # result is dict {ticker: price}
            prices = {t: [float(result["content"][0]["text"].get(t, 0))] for t in tickers}
            return prices

    def _fetch_from_yfinance(self, tickers: List[str]) -> Dict[str, List[float]]:
        prices: Dict[str, List[float]] = {}
        for t in tickers:
            try:
                df = yf.download(
                    t + ".NS", period="1mo", interval="1d",
                    progress=False, auto_adjust=True
                )
                if df is not None and len(df):
                    close_series = df["Close"]
                    arr = close_series.values.flatten().tolist()
                    prices[t] = arr[-30:]
            except Exception:
                pass
        return prices

    def _fallback_synthetic(self, tickers: List[str]) -> Dict[str, List[float]]:
        prices: Dict[str, List[float]] = {}
        for t in tickers:
            base = 1000 + random.random() * 200
            series = [base]
            for _ in range(29):
                series.append(series[-1] * (1 + random.gauss(0.0005, 0.01)))
            prices[t] = series
        return prices

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        tickers = list(state.get("current_alloc", {}).keys()) or \
                  ["RELIANCE", "TCS", "HDFCBANK", "INFY"]

        prices: Dict[str, List[float]] = {}
        source_used = "unknown"

        # --- 1) Try MCP (async) ---
        if ClientSession is not None:
            import asyncio
            try:
                prices = asyncio.run(self._fetch_from_mcp(tickers))
                if prices:
                    source_used = "MCP"
            except Exception as e:
                state["messages"].append(AIMessage(
                    content=f"[MarketDataAgent] MCP fetch failed: {e}. Falling back to yfinance."
                ))

        # --- 2) Try yfinance ---
        if not prices:
            prices = self._fetch_from_yfinance(tickers)
            if prices:
                source_used = "yfinance"

        # --- 3) Synthetic fallback ---
        if not prices:
            prices = self._fallback_synthetic(tickers)
            source_used = "synthetic"

        # --- Attach results to state ---
        start_date = (datetime.date.today() - datetime.timedelta(days=29)).strftime("%Y-%m-%d")
        end_date = datetime.date.today().strftime("%Y-%m-%d")

        state["tickers"] = tickers
        state["prices"] = prices
        state["date_range"] = {"start": start_date, "end": end_date}
        state["messages"].append(
            AIMessage(content=f"[MarketDataAgent] Prices for {tickers} from {start_date} → {end_date} (source: {source_used})")
        )
        return state
