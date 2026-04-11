import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="💭 Sentiment Analysis", layout="wide")

def main():
    st.title("💭 Sentiment Analysis")
    
    # Dummy data untuk demo
    st.info("📊 Data sentiment adalah simulasi untuk demo")
    
    # COT Report
    st.header("📊 COT Report")
    cot_df = pd.DataFrame({
        "Currency": ["EUR", "GBP", "JPY", "AUD"],
        "Net Position": [60000, 17000, -53000, 7000],
        "Signal": ["🟢 Bullish", "🟡 Neutral", "🔴 Bearish", "🟢 Bullish"]
    })
    st.dataframe(cot_df, use_container_width=True, hide_index=True)
    
    # Fear & Greed
    st.header("😨😋 Fear & Greed Index")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=53,
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1f77b4"}}
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 Retail sentiment bersifat contrarian. >65% Long = potensi reversal.")

if __name__ == "__main__":
    main()
