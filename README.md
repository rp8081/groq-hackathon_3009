# 📈 Finance Agent – Multi-Modal Portfolio Rebalancer 💸

An advanced **LangGraph + LangChain-Groq** powered **Finance Agent** that helps you **analyze, rebalance, and simulate portfolios** with **agentic workflows**.

Enhanced with **MCP (Model Connection Protocol)** support for seamless external tool integration (e.g., live market data) and **multi-modal input** (text + voice).

---

## ✨ Key Features

### 🧩 Multi-Agent Workflow (LangGraph) 🧠
The system uses a sophisticated **multi-agent architecture** orchestrated by LangGraph to handle complex financial tasks:

| Agent | Purpose |
| :--- | :--- |
| **PortfolioInputAgent** | Parses portfolio allocations from user input. |
| **MarketDataAgent** | Fetches historical prices (via yfinance / MCP server). |
| **RiskAgent** | Computes risk metrics (volatility, VaR, drawdown). |
| **PortfolioAgent** | Suggests rebalancing allocations. |
| **ExecutionAgent** | Simulates trade orders. |
| **GenericAgent** | Answers open-ended financial questions (e.g., *"Should I quit the stock market?"*). |
| **Supervisor** | Orchestrates the flow, ensuring efficiency and avoiding infinite loops. |

---

### ⚡ Groq LLM Integration (Ultra-Low Latency) 🚀
- Uses **Groq-hosted models (`gemma2-9b-it`)** for reasoning and parsing.
- Achieves **ultra-low latency inference** for real-time agent responses.

---

### 🎙️ Multi-Modal Input & Visualization 📊
| Feature | Status | Description |
| :--- | :--- | :--- |
| **Text Input** | ✅ Working | Standard input for portfolio or queries. |
| **Voice Input** | ✅ Working | 🎤 Speak your portfolio or question → **Whisper transcription** → editable text → full agent flow. |
| **Visualization** | Included | Built-in charting (**matplotlib**) to visualize stock history. |
| **Agent Trace** | Included | Detailed agent trace view with **emoji-coded step outputs** for transparency. |
| **Orders Export** | Included | Final trade orders exportable to **CSV**. |

---

### 🌐 MCP (Model Connection Protocol) Integration 🔗

**MCP** allows the Finance Agent to use external services as first-class tools, cleanly separating reasoning logic (LLM) from data sources (MCP tools).

- **Decoupled Data:** Market data can be served from an MCP server (`mcp_market_server.py`).
- **Seamless Tooling:** Agent fetches latest stock prices **without hardcoding APIs**.

#### Example Workflow with MCP

1.  **Start MCP Market Data Server:**
    ```bash
    python mcp_market_server.py
    # Prints endpoint like: http://localhost:7860/gradio_api/mcp/sse
    ```
2.  **Export the Endpoint:**
    ```bash
    export MCP_MARKET_ENDPOINT=http://localhost:7860/gradio_api/mcp/sse
    ```
3.  **Run Finance Agent:**
    ```bash
    python -m src.app
    # MarketDataAgent now fetches prices via MCP seamlessly!
    ```

---

## 🛠️ Extensibility & Project Structure

### 🔧 Extensibility
- **Modular Code Design** (`src/agents/`, `src/utils/`, `src/plotter.py`).
- **Plug-and-play** new agents (e.g., compliance, broker API, sentiment analysis).
- Built with **LangGraph** for easy extension of nodes & flows.

### 📂 Project Structure
```text
finance_agent/
│── src/
│   ├── app.py                  # Gradio UI entry point
│   ├── graph_builder.py        # LangGraph workflow
│   ├── plotter.py              # Price chart generator
│   ├── agents/
│   │   ├── supervisor.py       # Supervisor logic
│   │   ├── portfolio_input.py  # Portfolio parsing agent
│   │   ├── market_data.py      # Market data agent (yfinance + MCP)
│   │   ├── risk.py             # Risk metrics agent
│   │   ├── portfolio.py        # Rebalancing agent
│   │   ├── execution.py        # Trade simulation agent
│   │   └── generic_agent.py    # Handles open-ended financial queries
│   └── utils/
│       └── modality_preprocessors.py   # Voice → Text pipeline
│── mcp_market_server.py        # MCP server exposing `get_prices`
│── mcp_market_client.py        # Example MCP client
│── requirements.txt
│── README.md



