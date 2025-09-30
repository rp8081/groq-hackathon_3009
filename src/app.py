import os
import gradio as gr
import pandas as pd
import speech_recognition as sr
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

from .graph_builder import build_finance_graph
from .plotter import plot_prices

# ---------------- Setup ----------------
load_dotenv()
MODEL_NAME = "gemma2-9b-it"
llm = ChatGroq(model=MODEL_NAME, api_key=os.getenv("GROQ_API_KEY"))
graph = build_finance_graph(llm)

recognizer = sr.Recognizer()

def transcribe_voice(audio_file):
    """Transcribe voice -> text"""
    if not audio_file:
        return ""
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except Exception as e:
        return f"[Transcription error: {e}]"

# ---------------- Existing Pipeline ----------------
def run_portfolio(user_input):
    state = {"messages": [HumanMessage(content=user_input)]}
    final_state = graph.invoke(state, config={"recursion_limit": 50})

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
        elif "[GenericAgent]" in content:
            trace_lines.append(f"🟡 GenericAgent → {content}")
        else:
            trace_lines.append(f"👤 User/Supervisor → {content}")
    trace_lines.append("✅ Supervisor → DONE (workflow complete)")

    orders = final_state.get("orders", [])
    if orders:
        df_orders = pd.DataFrame(orders)
    else:
        df_orders = pd.DataFrame(
            [{"ticker": "-", "side": "No Action", "notional": "-", "quantity": "-"}]
        )
    return "\n".join(trace_lines), df_orders, final_state

def run_and_plot(user_input):
    trace, df_orders, final_state = run_portfolio(user_input)
    chart = plot_prices(final_state)
    csv_path = "orders.csv"
    df_orders.to_csv(csv_path, index=False)
    return trace, df_orders, chart, csv_path

# ---------------- Gradio UI ----------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## 🎤📈 Portfolio / Generic Query Agent (Text or Voice)")

    with gr.Row():
        mode = gr.Radio(["Text", "Voice"], value="Text", label="Input Mode")

    with gr.Row():
        inp_text = gr.Textbox(
            label="Your Input",
            placeholder="Type portfolio like: RELIANCE 40, TCS 30, INFY 20 OR ask: Is Infosys good?",
            lines=2,
            scale=3,
        )
        inp_voice = gr.Audio(sources=["microphone"], type="filepath", label="🎤 Record Voice", scale=2)

    with gr.Row():
        transcribe_btn = gr.Button("📝 Transcribe Voice")
        run_btn = gr.Button("🚀 Run Analysis")
        combo_btn = gr.Button("⚡ Run + Plot")

    with gr.Row():
        trace = gr.Textbox(label="Agent Trace", lines=15)

    with gr.Row():
        orders = gr.Dataframe(label="Final Orders", interactive=False)

    with gr.Row():
        chart = gr.Plot(label="Price History")

    with gr.Row():
        download = gr.File(label="⬇️ Download Orders as CSV")

    # --- Logic wiring ---
    def transcribe_and_fill(audio_file):
        return transcribe_voice(audio_file)

    transcribe_btn.click(transcribe_and_fill, inputs=[inp_voice], outputs=[inp_text])

    run_btn.click(
        lambda user_input: run_portfolio(user_input)[:2],
        inputs=[inp_text],
        outputs=[trace, orders],
    )

    combo_btn.click(
        run_and_plot, inputs=[inp_text], outputs=[trace, orders, chart, download]
    )

if __name__ == "__main__":
    demo.launch()
