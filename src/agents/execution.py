from langchain_core.messages import AIMessage
from typing import Dict, Any


class ExecutionAgent:
    name = "ExecutionAgent"

    def __init__(self, llm=None, notional: float = 100000.0):
        self.llm = llm
        self.notional = notional   # total portfolio value in INR

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        current = state.get("current_alloc", {})
        target = state.get("target_alloc", {})
        tickers = list(set(current.keys()) | set(target.keys()))
        prices = state.get("prices", {})

        orders = []
        for t in tickers:
            cur_w = current.get(t, 0.0)
            tar_w = target.get(t, 0.0)
            diff = round(tar_w - cur_w, 4)

            if abs(diff) > 0.01:  # only rebalance if >1% difference
                direction = "BUY" if diff > 0 else "SELL"
                order_notional = round(abs(diff) * self.notional, 2)

                qty = None
                if t in prices and prices[t]:
                    last_price = prices[t][-1]
                    qty = int(order_notional / last_price)

                orders.append({
                    "ticker": t,
                    "side": direction,
                    "notional": order_notional,
                    "quantity": qty
                })

        # ✅ always set orders, even if empty
        state["orders"] = orders

        # ✅ bump execution counter
        state["execution_count"] = state.get("execution_count", 0) + 1

        state["messages"].append(
            AIMessage(content=f"[ExecutionAgent] Generated orders: {orders}")
        )
        return state
