from langchain_core.messages import AIMessage
from typing import Dict, Any

class PortfolioAgent:
    name = "PortfolioAgent"

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        risk = state.get("risk", {})
        per_ticker = risk.get("by_ticker", {})
        prices = state.get("prices", {})

        if per_ticker:
            inv_vars = {}
            for t, metrics in per_ticker.items():
                vol = metrics.get("vol_annualized", 0.0)
                var = vol**2 if vol > 0 else 1.0
                inv_vars[t] = 1.0/var if var > 1e-12 else 0.0
            total = sum(inv_vars.values()) or 1.0
            weights = {t: w/total for t, w in inv_vars.items()}
        elif prices:
            n = len(prices)
            weights = {t: 1.0/n for t in prices} if n else {}
        else:
            weights = {}

        weights = {t: round(w, 4) for t, w in weights.items()}
        state["target_alloc"] = weights
        state["messages"].append(AIMessage(content=f"[PortfolioAgent] Suggested allocation based on inverse variance: {weights}"))
        return state
