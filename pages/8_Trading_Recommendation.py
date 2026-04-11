import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.api_utils import fallback_to_frankfurter
    from utils.indicators import calculate_all_indicators
    from utils.calculations import calculate_position_size
except ImportError:
    def fallback_to_frankfurter(*args, **kwargs):
        dates = pd.date_range(end=datetime.now(), periods=60, freq="D")
        close = [1.0850 * (1 + i * 0.0001) for i in range(60)]
        df = pd.DataFrame({"Date": dates, "Close": close})
        df.set_index("Date", inplace=True)
        df["open"] = df["Close"] - 0.0001
        df["high"] = df["Close"] + 0.0002
        df["low"] = df["Close"] - 0.0002
        df["close"] = df["Close"]
        df["atr_14"] = 0.001
        return df
    
    def calculate_all_indicators(df):
        df["atr_14"] = 0.001
        return df
    
    def calculate_position_size(balance, risk_pct, sl_pips, pip_val=10):
        return round((balance * (risk_pct/100)) / (sl_pips * pip_val), 2)

st.set_page_config(page_title="🎯 Trading Recommendation", layout="wide")

def main():
    st.title("🎯 Trading Recommendation")
    
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    # Risk Profile Selection
    scenario = st.radio(
        "Risk Profile",
        ["Conservative", "Moderate", "Aggressive"],
        horizontal=True
    )
    
    mult = {"Conservative": 2.5, "Moderate": 1.5, "Aggressive": 1.0}[scenario]
    
    # Fetch data
    df = fallback_to_frankfurter(pair, days=50)
    
    if not df.empty:
        df = calculate_all_indicators(df)
        latest = df.iloc[-1]
        price = latest["close"]
        atr = latest.get("atr_14", 0.001)
        
        # Calculate levels
        sl_dist = atr * mult
        sl = price - sl_dist if price > df.iloc[-2]["close"] else price + sl_dist
        tp1 = price + (abs(price - sl) * 2) if sl < price else price - (abs(sl - price) * 2)
        tp2 = price + (abs(price - sl) * 3) if sl < price else price - (abs(sl - price) * 3)
        
        # Display levels
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Entry", f"{price:.5f}")
        c2.metric("Stop Loss", f"{sl:.5f}")
        c3.metric("TP 1", f"{tp1:.5f}")
        c4.metric("TP 2", f"{tp2:.5f}")
        
        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["close"], name="Price", line=dict(color="white")))
        fig.add_hline(y=price, line_dash="dash", line_color="gold", annotation_text="Entry")
        fig.add_hline(y=sl, line_dash="dot", line_color="red", annotation_text="SL")
        fig.add_hline(y=tp1, line_dash="dot", line_color="green", annotation_text="TP1")
        fig.add_hline(y=tp2, line_dash="dot", line_color="lime", annotation_text="TP2")
        fig.update_layout(
            title=f"{pair} - Trade Setup",
            height=350,
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk Calculator
        st.markdown("### 💰 Risk Calculator")
        
        bal = st.session_state.get("account_balance", 10000)
        risk = st.session_state.get("risk_per_trade", 1.0)
        
        pips = abs(price - sl) / 0.0001
        lots = calculate_position_size(bal, risk, pips, 10)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Position Size", f"{lots:.2f} lots")
        c2.metric("Risk Amount", f"${bal * (risk / 100):,.2f}")
        c3.metric("Risk:Reward", f"1:{abs(tp1-price)/abs(price-sl):.1f}")
        
        # Trade Plan
        st.markdown("### 📋 Trade Plan")
        
        direction = "BUY" if sl < price else "SELL"
        rr_ratio = abs(tp1 - price) / abs(price - sl)
        
        plan_df = pd.DataFrame({
            "Parameter": ["Pair", "Direction", "Entry Price", "Stop Loss", "Take Profit 1", "Take Profit 2", "Risk:Reward"],
            "Value": [
                pair,
                direction,
                f"{price:.5f}",
                f"{sl:.5f}",
                f"{tp1:.5f}",
                f"{tp2:.5f}",
                f"1:{rr_ratio:.1f}"
            ]
        })
        
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
        
        st.warning("""
        ⚠️ **DISCLAIMER**: Rekomendasi ini adalah simulasi untuk tujuan edukasi. 
        Selalu gunakan risk management yang ketat (max 1-2% per trade). 
        Trading forex berisiko tinggi terhadap modal Anda.
        """)
    
    else:
        st.warning("⚠️ Data tidak tersedia untuk generate rekomendasi.")

if __name__ == "__main__":
    main()