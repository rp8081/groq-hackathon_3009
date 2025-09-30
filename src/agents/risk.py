import numpy as np
from langchain_core.messages import AIMessage
from typing import Dict, Any

def simple_returns(prices):
    if len(prices) < 2:
        return []
    return [(p2 - p1)/p1 for p1, p2 in zip(prices[:-1], prices[1:])]

def annualized_vol(returns, factor=252):
    return float(np.std(returns) * np.sqrt(factor)) if returns else 0.0

def var_95(returns, alpha=0.95):
    return float(np.quantile(returns, 1 - alpha)) if returns else 0.0

def max_drawdown(prices):
    if not prices:
        return 0.0
    peak = prices[0]
    dd = 0.0
    for p in prices:
        peak = max(peak, p)
        dd = min(dd, p/peak - 1.0)
    return float(dd)

class RiskAgent:
    name = "RiskAgent"

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        prices = state.get("prices", {})
        returns_by_ticker = {t: simple_returns(series) for t, series in prices.items()}

        per_ticker_risk = {}
        for t, rets in returns_by_ticker.items():
            per_ticker_risk[t] = {
                "vol_annualized": round(annualized_vol(rets), 4),
                "VaR95": round(var_95(rets), 4),
                "max_drawdown": round(max_drawdown(prices[t]), 4)
            }

        all_rets = [r for rs in returns_by_ticker.values() for r in rs]
        aggregate_risk = {
            "vol_annualized": round(annualized_vol(all_rets), 4),
            "VaR95": round(var_95(all_rets), 4),
            "max_drawdown": round(max((max_drawdown(ps) for ps in prices.values()), default=0.0), 4)
        }

        state["returns"] = returns_by_ticker
        state["risk"] = {"aggregate": aggregate_risk, "by_ticker": per_ticker_risk}
        state["messages"].append(AIMessage(content=f"[RiskAgent] Computed risk metrics: {state['risk']}"))
        return state
