import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="🤖 AI Analysis Scoring", layout="wide")

def main():
    st.title("🤖 AI Analysis & Hybrid Scoring")
    
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    # Simulated scores
    tech_score = 65
    fund_score = 50
    sent_score = 55
    hybrid_score = round(tech_score * 0.5 + fund_score * 0.3 + sent_score * 0.2, 1)
    
    # Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Technical", f"{tech_score}/100")
    col2.metric("Fundamental", f"{fund_score}/100")
    col3.metric("Sentiment", f"{sent_score}/100")
    col4.metric("Hybrid", f"{hybrid_score}/100")
    
    # Progress bars
    st.progress(hybrid_score / 100)
    
    # Insight
    if hybrid_score >= 60:
        st.success(f"🟢 **BUY Signal** untuk {pair}")
    elif hybrid_score <= 40:
        st.error(f"🔴 **SELL Signal** untuk {pair}")
    else:
        st.warning(f"⚪ **WAIT** untuk {pair}")
    
    st.info("💡 Hybrid Score = Technical(50%) + Fundamental(30%) + Sentiment(20%)")

if __name__ == "__main__":
    main()
