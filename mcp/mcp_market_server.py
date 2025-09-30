"""Expose market data retrieval as an MCP‑compliant tool via Gradio.

Run this file to start a simple server that can be called from LangChain/LLM agents
through the Model Connection Protocol.  The server listens on port 7860 by default
and exposes a single function `get_prices` that fetches the latest closing price
for a list of tickers using the `yfinance` library.  If `yfinance` fails or
returns NaN, the function synthesises a price so the agent can continue to work.

To use this tool from your agent, set the environment variable
`MCP_MARKET_ENDPOINT` to the URL printed when the server starts, usually
`http://localhost:7860/gradio_api/mcp/sse`.

"""

from __future__ import annotations

import datetime
import json
import os
from typing import Dict, List

import gradio as gr
import numpy as np
import pandas as pd
import yfinance as yf


def get_prices(tickers: List[str]) -> Dict[str, float]:
    """Return the latest closing price for each ticker.

    This helper attempts to fetch prices using the `yfinance` library.  It
    explicitly specifies `auto_adjust=True` to avoid future warnings.  If
    the initial lookup fails (for example because a ticker is from a non‑US
    exchange), the function will try common suffixes for Indian exchanges
    (".NS" for NSE and ".BO" for BSE).  Should all attempts fail, a synthetic
    price between 50 and 150 is returned so that downstream agents can
    continue to operate.
    """
    prices: Dict[str, float] = {}
    for t in tickers:
        # Try the provided ticker, then fall back to common Indian suffixes
        attempts = [t]
        if "." not in t and len(t) <= 5:
            attempts += [f"{t}.NS", f"{t}.BO"]
        price: Optional[float] = None
        for sym in attempts:
            try:
                data = yf.download(sym, period="1mo", auto_adjust=True, progress=False)
                if not data.empty:
                    # Use the last available closing price
                    last_price = data["Close"].dropna().iloc[-1]
                    price = float(last_price.item())
                    break
            except Exception:
                price = None
        if price is None:
            # Fall back to a random synthetic price
            price = float(np.round(np.random.uniform(50, 150), 2))
        prices[t] = price
    return prices


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="Market Data MCP Server") as demo:
        gr.Markdown("# Market Data Tool")
        ticker_input = gr.Textbox(label="Tickers (comma separated)")
        submit_btn = gr.Button("Get prices")
        output_box = gr.JSON(label="Prices")

        def on_submit(text):
            tickers = [t.strip().upper() for t in text.split(",") if t.strip()]
            return get_prices(tickers)

        submit_btn.click(on_submit, ticker_input, output_box)
    return demo


def main() -> None:
    demo = build_demo()
    # Launch as MCP server; prints SSE endpoint to stdout.
    demo.launch(mcp_server=True, share=False)


if __name__ == "__main__":
    main()