from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from typing import Dict, Any


class Supervisor:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(
            "You are the Supervisor. Decide the next agent.\n"
            "Options: portfolioinput | market | risk | portfolio | execution | generic | done\n"
            "Rules:\n"
            "- If no current_alloc -> portfolioinput\n"
            "- If no prices -> market\n"
            "- If no risk -> risk\n"
            "- If no target_alloc -> portfolio\n"
            "- If no orders -> execution\n"
            "- Else -> done\n\n"
            "State: {state}\n"
            "User goal: {goal}"
        )

    def route(self, state: Dict[str, Any]) -> str:
        goal = ""
        msgs = state.get("messages") or []
        if msgs:
            last = msgs[-1]
            goal = getattr(last, "content", str(last))

        # Track attempts
        state["_portfolio_attempts"] = state.get("_portfolio_attempts", 0)
        state["_execution_attempts"] = state.get("_execution_attempts", 0)

        # ✅ Detect if input looks like a portfolio (at least 1 digit + 1 known ticker)
        known_tickers = {"RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "HINDUNILVR"}
        has_digit = any(ch.isdigit() for ch in goal)
        has_known_ticker = any(t in goal.upper() for t in known_tickers)
        looks_like_portfolio = has_digit and has_known_ticker

        # If not portfolio → GenericAgent
        if not looks_like_portfolio:
            return "generic"

        # ✅ Prevent infinite loops
        if state["_portfolio_attempts"] >= 3 and not state.get("current_alloc"):
            state["messages"].append(
                HumanMessage(content="[Supervisor] Stopping after 3 failed portfolio parsing attempts.")
            )
            return "done"

        if state["_execution_attempts"] >= 2 and state.get("orders") is None:
            state["messages"].append(
                HumanMessage(content="[Supervisor] Stopping after 2 failed execution attempts.")
            )
            return "done"

        # Try LLM routing
        try:
            msg = self.prompt.format(
                state=str({
                    "has_alloc": bool(state.get("current_alloc")),
                    "has_prices": bool(state.get("prices")),
                    "has_risk": bool(state.get("risk")),
                    "has_target": bool(state.get("target_alloc")),
                    "has_orders": state.get("orders") is not None,
                }),
                goal=goal
            )
            out = self.llm.invoke([HumanMessage(content=str(msg))])
            token = getattr(out, "content", "").strip().lower()
            if token in {"portfolioinput", "market", "risk", "portfolio", "execution", "generic", "done"}:
                return token
        except Exception:
            pass

        # ✅ Fallback deterministic rules
        if not state.get("current_alloc"):
            state["_portfolio_attempts"] += 1
            return "portfolioinput"
        if not state.get("prices"):
            return "market"
        if not state.get("risk"):
            return "risk"
        if not state.get("target_alloc"):
            return "portfolio"
        if state.get("orders") is None:
            state["_execution_attempts"] += 1
            return "execution"

        return "done"
