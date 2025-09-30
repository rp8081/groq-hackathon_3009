"""Example client for calling the `get_prices` tool exposed by `mcp_market_server.py`.

This script demonstrates how a LangChain agent or standalone Python program can
invoke an MCP tool.  It uses the `langchain_mcp` library to manage the
connection and tool invocation.  Before running, ensure that the market server
is running and that the environment variable `MCP_MARKET_ENDPOINT` is set to
the endpoint printed by the server (e.g. `http://localhost:7860/gradio_api/mcp/sse`).

Usage:

```bash
python mcp_market_client.py AAPL MSFT
```
"""

import asyncio
import os
import sys
from typing import List

try:
    from langchain_mcp import ClientSession  # type: ignore
except ImportError as e:
    raise ImportError(
        "langchain_mcp is not installed.  Install it with `pip install langchain-mcp`."
    ) from e


async def main(tickers: List[str]) -> None:
    endpoint = os.environ.get("MCP_MARKET_ENDPOINT")
    if not endpoint:
        raise RuntimeError(
            "MCP_MARKET_ENDPOINT environment variable not set.  "
            "Start the server and copy the printed endpoint into this variable."
        )
    async with ClientSession(endpoint=endpoint) as session:
        result = await session.call_tool("get_prices", {"tickers": tickers})
        print(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_market_client.py <TICKER1> [<TICKER2> ...]")
        sys.exit(1)
    asyncio.run(main([t.upper() for t in sys.argv[1:]]))