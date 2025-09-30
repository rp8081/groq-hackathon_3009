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
| **Text Input** | ✅ Included | Standard input for portfolio or queries. |
| **Voice Input** | ✅ Included | 🎤 Speak your portfolio or question → **Whisper transcription** → editable text → full agent flow. |
| **Visualization** | ✅ Included | Built-in charting (**matplotlib**) to visualize stock history. |
| **Agent Trace** | ✅ Included | Detailed agent trace view with **emoji-coded step outputs** for transparency. |
| **Orders Export** | ✅ Included | Final trade orders exportable to **CSV**. |

---

### 🌐 MCP (Model Connection Protocol) Integration 🔗
**MCP** allows the Finance Agent to use external services as first-class tools, cleanly separating reasoning logic (LLM) from data sources (MCP tools).

- **Decoupled Data:** Market data can be served from an MCP server (`mcp_market_server.py`).
- **Seamless Tooling:** Agent fetches latest stock prices **without hardcoding APIs**.

#### Example Workflow with MCP
1. **Start MCP Market Data Server:**
    ```bash
    python mcp_market_server.py
    # Prints endpoint like: http://localhost:7860/gradio_api/mcp/sse
    ```
2. **Export the Endpoint:**
    ```bash
    export MCP_MARKET_ENDPOINT=http://localhost:7860/gradio_api/mcp/sse
    ```
3. **Run Finance Agent:**
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
- **MCP support** → connect to external services (prices, news, compliance APIs).

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
│── mcp/
│   ├── mcp_market_server.py    # MCP server exposing `get_prices`
│   └── mcp_market_client.py    # Example MCP client
│── requirements.txt
│── README.md
```

---

## ⚡ Usage
```bash
# Clone repo
git clone https://github.com/yourusername/finance_agent.git
cd finance_agent

# Create venv
python -m venv venv
venv\Scripts\activate      # Windows
# or source venv/bin/activate (Linux/Mac)

# Install dependencies
pip install -r requirements.txt

# Start MCP server first
python mcp_market_server.py

# Run Finance Agent
python -m src.app
```

---

## 🔍 Example Trace (Portfolio Workflow)
**Input:**
```text
RELIANCE 40, TCS 30, HDFCBANK 20, INFY 10
```

**Output:**
```
👤 User/Supervisor → RELIANCE 40, TCS 30, HDFCBANK 20, INFY 10
🟢 PortfolioInputAgent → Parsed allocations: {'RELIANCE': 0.4, 'TCS': 0.3, 'HDFCBANK': 0.2, 'INFY': 0.1}
🔵 MarketDataAgent → Prices fetched from 2024-09-01 → 2024-09-30
🟠 RiskAgent → Computed risk metrics: {...}
🟣 PortfolioAgent → Suggested allocation based on inverse variance: {...}
🟤 ExecutionAgent → Generated orders: [...]
✅ Supervisor → DONE (workflow complete)
```

---

## 🔍 Example Trace (Generic Questions)
The **GenericAgent** uses Groq LLM + Wikipedia + market data to answer broader queries.

**Examples:**
```text
"Is TCS a good company to invest in?"
"Compare TCS vs Infosys."
"Should I quit the stock market?"
```

**Output Example:**
```
👤 User/Supervisor → Is TCS a good company to invest in?
🟡 GenericAgent → [GenericAgent] Provides structured answer with positives, risks, recent returns (yfinance), Wikipedia context, and a disclaimer.
✅ Supervisor → DONE (workflow complete)
```

---

## ✅ Why This Project Matters
- **LLM-powered reasoning** for both structured portfolio tasks and open-ended financial queries.
- **MCP-enabled tools** → external services can be added without breaking core logic.
- **Multi-modal support** (Text + Voice) for maximum flexibility.
- **Clear visualization and agent traces** to improve trust & debugging.
- **Built to be extensible and production-ready.**
