import datetime
from typing import Dict, Any, Optional

import yfinance as yf
from langchain_core.messages import AIMessage, HumanMessage
from langchain.llms.base import LLM
from langchain.utilities import WikipediaAPIWrapper

TICKER_TO_NAME = {
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "RELIANCE": "Reliance Industries",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank",
    "SBIN": "State Bank of India",
    "HINDUNILVR": "Hindustan Unilever"
}


class GenericAgent:
    name = "GenericAgent"

    def __init__(self, llm: Optional[LLM] = None):
        self.llm = llm
        self.wiki = WikipediaAPIWrapper()

    def _detect_ticker(self, query: str) -> Optional[str]:
        u = query.upper()
        for t in TICKER_TO_NAME.keys():
            if t in u or TICKER_TO_NAME[t].upper() in u:
                return t
        return None

    def _fetch_returns(self, ticker: str) -> Optional[float]:
        try:
            df = yf.download(ticker + ".NS", period="3mo", interval="1d",
                             progress=False, auto_adjust=True)
            if df is None or df.empty:
                return None
            start = df["Close"].iloc[0]
            end = df["Close"].iloc[-1]
            return float((end / start - 1.0) * 100.0)
        except Exception:
            return None

    def _fetch_wiki_summary(self, company_name: str) -> str:
        try:
            return self.wiki.run(company_name)
        except Exception:
            return ""

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        msgs = state.get("messages") or []
        query = getattr(msgs[-1], "content", str(msgs[-1])) if msgs else ""

        ticker = self._detect_ticker(query)
        company_name = TICKER_TO_NAME.get(ticker) if ticker else None

        answer_text = ""

        # 🟢 Case 1: Ticker detected → structured flow
        if ticker:
            ret_val = self._fetch_returns(ticker)
            returns_summary = (
                f"{ticker} 3-month return: {ret_val:.2f}%"
                if ret_val is not None else "No recent return data available"
            )
            wiki_summary = self._fetch_wiki_summary(company_name) if company_name else ""

            llm_prompt = f"""
User query: {query}

Company: {company_name}
Market data: {returns_summary}
Wikipedia summary: {wiki_summary or "N/A"}

Task: Answer as an investment advisor.
Sections:
1. Short direct answer (Yes/No/Maybe).
2. Positives.
3. Negatives.
4. Data summary.
5. Simple takeaway.
Include a disclaimer at the end.
"""
            try:
                resp = self.llm.invoke([HumanMessage(content=llm_prompt)])
                answer_text = getattr(resp, "content", str(resp))
            except Exception as e:
                answer_text = f"GenericAgent error: {e}"

        # 🟡 Case 2: No ticker → use LLM directly (general-investing mode)
        else:
            llm_prompt = f"""
User query: {query}

Task: Respond as a rational investment advisor.
- Give a clear answer in plain English.
- Organize response into: (1) Short answer, (2) Supporting reasons, (3) Risks/uncertainties, (4) Simple investor takeaway.
- Add a one-line disclaimer.
"""
            try:
                resp = self.llm.invoke([HumanMessage(content=llm_prompt)])
                answer_text = getattr(resp, "content", str(resp))
            except Exception as e:
                answer_text = f"GenericAgent error: {e}"

        # Append to state
        state["messages"].append(AIMessage(content=f"[GenericAgent] {answer_text}"))
        state["generic_answer"] = {"answer_text": answer_text, "ticker": ticker}

        return state
