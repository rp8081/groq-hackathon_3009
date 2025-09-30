from langgraph.graph import StateGraph, START, END
from .state import FinanceState
from .agents import (
    Supervisor,
    PortfolioInputAgent,
    MarketDataAgent,
    RiskAgent,
    PortfolioAgent,
    ExecutionAgent,
    GenericAgent,
)


def build_finance_graph(llm):
    sup = Supervisor(llm)

    # ✅ Supervisor node returns routing decision
    def supervisor_node(state: FinanceState) -> dict:
        decision = sup.route(state)
        return {"_next": decision}

    # ✅ Wrapper node to mark workflow done
    def done_node(state: FinanceState) -> dict:
        # add a final trace marker
        messages = state.get("messages", [])
        messages.append({"type": "system", "content": "✅ Supervisor → DONE (workflow complete)"})
        state["messages"] = messages
        return state

    graph = StateGraph(FinanceState)

    # --- Nodes ---
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("portfolioinput", PortfolioInputAgent(llm).run)
    graph.add_node("market", MarketDataAgent(llm).run)
    graph.add_node("risk", RiskAgent(llm).run)
    graph.add_node("portfolio", PortfolioAgent(llm).run)
    graph.add_node("execution", ExecutionAgent(llm).run)
    graph.add_node("generic", GenericAgent(llm).run)
    graph.add_node("done", done_node)

    # --- Edges ---
    graph.add_edge(START, "supervisor")

    # Conditional routes decided by supervisor
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["_next"],
        {
            "portfolioinput": "portfolioinput",
            "market": "market",
            "risk": "risk",
            "portfolio": "portfolio",
            "execution": "execution",
            "generic": "generic",
            "done": "done",   # go to done node
        }
    )

    # Portfolio workflow loops back to supervisor
    for node in ["portfolioinput", "market", "risk", "portfolio", "execution"]:
        graph.add_edge(node, "supervisor")

    # ✅ Generic agent is terminal: goes directly to done
    graph.add_edge("generic", "done")

    # ✅ Done node ends workflow
    graph.add_edge("done", END)

    return graph.compile()
