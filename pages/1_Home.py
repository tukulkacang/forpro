import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys, os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports
try:
    from utils.api_utils import fallback_to_frankfurter
    from utils.indicators import calculate_all_indicators
    from utils.helpers import add_disclaimer
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
        return df
    
    def calculate_all_indicators(df):
        if "close" in df.columns:
            df["sma_20"] = df["close"].rolling(20).mean()
            df["rsi_14"] = 50.0
            df["atr_14"] = 0.001
        return df
    
    def add_disclaimer():
        st.warning("⚠️ **DISCLAIMER**: Untuk tujuan edukasi. Trading forex berisiko tinggi.")

st.set_page_config(page_title="🏠 Home", layout="wide")

def main():
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    st.title("🏠 Dashboard Overview")
    
    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pairs Tracked", "10+")
    c2.metric("Indicators", "100+")
    c3.metric("Strategies", "15+")
    c4.metric("AI Score", "Active")
    
    st.markdown("---")
    
    # Chart
    st.subheader(f"📈 Chart: {pair}")
    df = fallback_to_frankfurter(pair, days=60)
    
    if not df.empty and "close" in df.columns:
        df = calculate_all_indicators(df)
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price"
        )])
        
        if "sma_20" in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["sma_20"],
                name="SMA 20",
                line=dict(color="orange", width=1)
            ))
        
        fig.update_layout(
            title=f"{pair} - 60 Days Overview",
            yaxis_title="Price",
            xaxis_title="Date",
            height=500,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Price Info
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        change = ((latest["close"] - prev["close"]) / prev["close"]) * 100 if len(df) > 1 else 0
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.metric("Current Price", f"{latest['close']:.5f}", f"{change:+.3f}%")
        with col_p2:
            rsi_val = latest.get("rsi_14", 50)
            status = "Oversold" if rsi_val < 30 else "Overbought" if rsi_val > 70 else "Neutral"
            st.metric("RSI (14)", f"{rsi_val:.1f}", status)
        with col_p3:
            st.metric("ATR (14)", f"{latest.get('atr_14', 0):.5f}", "Volatility")
    else:
        st.warning("⚠️ Gagal memuat data chart.")
    
    st.markdown("---")
    
    # Market Overview
    st.subheader("🌍 Market Overview - Major Pairs")
    
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"]
    rows = []
    
    for p in pairs:
        d = fallback_to_frankfurter(p, days=2)
        if not d.empty and "close" in d.columns:
            cur = d.iloc[-1]["close"]
            prev = d.iloc[-2]["close"] if len(d) > 1 else cur
            chg = ((cur - prev) / prev) * 100
            
            trend = "🟢 Bullish" if chg > 0.1 else "🔴 Bearish" if chg < -0.1 else "⚪ Neutral"
            
            rows.append({
                "Pair": p,
                "Price": f"{cur:.5f}",
                "Change": f"{chg:+.3f}%",
                "Trend": trend
            })
    
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("⏳ Loading market data...")
    
    # Tips
    with st.expander("📚 Tips Trading - Elliott Wave + ICT"):
        st.markdown("""
        1. **Wave 2 Retracement** → Cari Bullish OB + FVG untuk entry Wave 3
        2. **Wave 4 Retracement** → Cari Bearish OB + FVG untuk entry Wave 5
        3. **Entry**: Di Order Block + BOS confirmation
        4. **SL**: Di luar OB atau Liquidity Pool
        5. **TP**: Fib extension 1.272/1.618
        """)
    
    st.markdown("---")
    st.subheader("⚡ Quick Navigation")
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        if st.button("📊 Live Rates", use_container_width=True):
            st.switch_page("pages/2_Live_Rates.py")
    with col_nav2:
        if st.button("📈 Technical Analysis", use_container_width=True):
            st.switch_page("pages/3_Technical_Analysis.py")
    with col_nav3:
        if st.button("🚀 Trading Strategies", use_container_width=True):
            st.switch_page("pages/6_Trading_Strategies.py")
    
    add_disclaimer()

if __name__ == "__main__":
    main()