import matplotlib
matplotlib.use("Agg")   # ✅ non-GUI backend for Gradio

import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any


def plot_prices(final_state: Dict[str, Any]):
    """
    Plot the price history from the final_state.
    """
    prices = final_state.get("prices", {})
    if not prices:
        return None

    df = pd.DataFrame(prices)
    fig, ax = plt.subplots(figsize=(8, 4))
    df.plot(ax=ax, title="Price History (last 1 month)")  # removed 📈 to avoid font warnings
    ax.set_xlabel("Days")
    ax.set_ylabel("Price (₹)")
    ax.legend(loc="best")
    plt.tight_layout()
    return fig
