import gradio as gr
import pandas as pd
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from .graph_builder import build_finance_graph
from .plotter import plot_prices


# ---------------- LLM + Graph ----------------
MODEL_NAME = "gemma2-9b-it"
llm = ChatGroq(api_key="YOUR_GROQ_KEY", model=MODEL_NAME)
graph = build_finance_graph(llm)


# ---------------- Pipeline ----------------
def run_portfolio(user_input):
    """Run the portfolio pipeline (agents only)."""
    state = {"messages": [HumanMessage(content=user_input)]}
    final_state = graph.invoke(state, config={"recursion_limit": 50})

    # Trace log (colored emojis per agent)
    trace_lines = []
    for msg in final_state["messages"]:
        content = msg.content
        if "[PortfolioInputAgent]" in content:
            trace_lines.append(f"🟢 PortfolioInputAgent → {content}")
        elif "[MarketDataAgent]" in content:
            trace_lines.append(f"🔵 MarketDataAgent → {content}")
        elif "[RiskAgent]" in content:
            trace_lines.append(f"🟠 RiskAgent → {content}")
        elif "[PortfolioAgent]" in content:
            trace_lines.append(f"🟣 PortfolioAgent → {content}")
        elif "[ExecutionAgent]" in content:
            trace_lines.append(f"🟤 ExecutionAgent → {content}")
        else:
            trace_lines.append(f"👤 User/Supervisor → {content}")

    # ✅ Add final supervisor decision explicitly
    trace_lines.append("✅ Supervisor → DONE (workflow complete)")

    # Orders as DataFrame
    orders = final_state.get("orders", [])
    if orders:
        df_orders = pd.DataFrame(orders)
    else:
        df_orders = pd.DataFrame(
            [{"ticker": "-", "side": "No Action", "notional": "-", "quantity": "-"}]
        )

    return "\n".join(trace_lines), df_orders, final_state


def plot_prices_from_input(user_input):
    """Run pipeline + plot price history."""
    _, _, final_state = run_portfolio(user_input)
    return plot_prices(final_state)


def run_and_plot(user_input):
    """Run pipeline + plot + prepare CSV download."""
    trace, df_orders, final_state = run_portfolio(user_input)
    chart = plot_prices(final_state)

    # Save CSV for download
    csv_path = "orders.csv"
    df_orders.to_csv(csv_path, index=False)

    return trace, df_orders, chart, csv_path


# ---------------- Gradio UI ----------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 📈 Portfolio Rebalancing Agent Demo")
    gr.Markdown(
        "Enter your portfolio like: `RELIANCE 40, TCS 30, HDFCBANK 20, INFY 10`"
    )

    with gr.Row():
        inp = gr.Textbox(
            label="Your Portfolio",
            placeholder="RELIANCE 40, TCS 30, HDFCBANK 20, INFY 10",
            scale=4,
        )
        run_btn = gr.Button("🚀 Run Analysis", scale=1)

    with gr.Row():
        plot_btn = gr.Button("📊 Plot Prices")
        combo_btn = gr.Button("⚡ Run + Plot Together")

    with gr.Row():
        trace = gr.Textbox(label="Agent Trace", lines=15)

    with gr.Row():
        orders = gr.Dataframe(label="Final Orders", interactive=False)

    with gr.Row():
        chart = gr.Plot(label="Price History")

    with gr.Row():
        download = gr.File(label="⬇️ Download Orders as CSV")

    # Button Actions
    run_btn.click(
        lambda user_input: run_portfolio(user_input)[:2],  # only trace + orders
        inputs=[inp],
        outputs=[trace, orders],
    )
    plot_btn.click(plot_prices_from_input, inputs=[inp], outputs=[chart])
    combo_btn.click(
        run_and_plot, inputs=[inp], outputs=[trace, orders, chart, download]
    )


if __name__ == "__main__":
    demo.launch()
