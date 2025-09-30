from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages


class FinanceState(TypedDict):
    messages: Annotated[list, add_messages]
    current_alloc: dict
    prices: dict
    date_range: dict
    returns: dict
    risk: dict
    target_alloc: dict
    orders: list
    execution_count: int   # ✅ new safety field
