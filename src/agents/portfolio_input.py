import json
import re
from typing import Dict, Any
from langchain_core.messages import AIMessage, HumanMessage


class PortfolioInputAgent:
    name = "PortfolioInputAgent"

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        msgs = state.get("messages") or []
        goal = getattr(msgs[-1], "content", str(msgs[-1])) if msgs else ""

        if not self.llm:
            state["messages"].append(AIMessage(content="[PortfolioInputAgent] No LLM configured."))
            return state

        # 🔒 strict JSON-only instruction
        prompt = f"""
You are a financial portfolio parser.

User input:
"{goal}"

Task:
- Extract all stock allocations from this input.
- Normalize company names to standard tickers:
  Reliance → RELIANCE
  Infosys → INFY
  Tata Consultancy Services / TCS → TCS
  HDFC Bank → HDFCBANK
  ICICI Bank → ICICIBANK
  State Bank of India / SBI → SBIN
  Hindustan Unilever → HINDUNILVR
- Return ONLY valid JSON. Do not add commentary.

Format:
{{
  "alloc": {{"RELIANCE": 30, "INFY": 40, "TCS": 60}}
}}
If nothing found, return:
{{ "alloc": {{}} }}
"""

        alloc = {}
        try:
            resp = self.llm.invoke([HumanMessage(content=prompt)])
            text = getattr(resp, "content", str(resp)).strip()

            # Ensure JSON block extraction
            match = re.search(r"\{[\s\S]*\}", text)
            if match:
                text = match.group(0)

            parsed = json.loads(text)
            alloc = parsed.get("alloc", {})
        except Exception as e:
            # Last-resort regex fallback
            for token in re.findall(r"([A-Z]{2,10})\s*(\d+)", goal.upper()):
                ticker, qty = token
                alloc[ticker] = int(qty)

        if alloc:
            total = sum(alloc.values())
            alloc_pct = {t: round(q / total, 4) for t, q in alloc.items()}
            state["current_alloc"] = alloc_pct
            state["messages"].append(AIMessage(content=f"[PortfolioInputAgent] Parsed allocations: {alloc_pct}"))
        else:
            state["messages"].append(AIMessage(content="[PortfolioInputAgent] No portfolio detected."))

        return state
