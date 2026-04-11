import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys, os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports dengan fallback aman
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

st.set_page_config(page_title="🏠 Home", layout="wide", initial_sidebar_state="collapsed")

# =============================================================================
# MOBILE RESPONSIVE CSS (OTOMATIS BIKIN RAPI DI HP)
# =============================================================================
st.markdown("""
<style>
    /* Otomatis stack kolom jadi vertikal di layar HP */
    @media (max-width: 768px) {
        .stColumns > div { 
            width: 100% !important; 
            display: block !important; 
            margin-bottom: 1rem !important; 
        }
        .stButton > button { 
            width: 100% !important; 
            margin-bottom: 0.5rem !important; 
        }
        div[data-testid="stMetric"] { 
            margin-bottom: 0.5rem !important; 
            padding: 0.5rem !important;
        }
        div[data-testid="stMetricValue"] { 
            font-size: 1.3rem !important; 
        }
        .main-header { 
            font-size: 1.8rem !important; 
        }
        /* Sidebar lebih rapi di mobile */
        section[data-testid="stSidebar"] {
            width: 280px !important;
        }
    }
    .main-header { 
        text-align: center; 
        font-size: 2.2rem; 
        font-weight: bold; 
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def _ensure_api_key():
    with st.sidebar:
        st.subheader("🔑 API Key")
        key_input = st.text_input("Twelve Data API Key", type="password",
                                  value=st.session_state.get("twelve_api_key", ""),
                                  key="sidebar_key_home")
        if key_input:
            st.session_state["twelve_api_key"] = key_input

def main():
    st.markdown('<p class="main-header">🏠 Dashboard Overview</p>', unsafe_allow_html=True)

    # Metrics (CSS akan otomatis stack di HP)
    c1, c2 = st.columns(2)
    c1.metric("Pairs Tracked", "10+")
    c2.metric("Indicators", "100+")
    c3, c4 = st.columns(2)
    c3.metric("Strategies", "15+")
    c4.metric("AI Score", "Active")

    st.markdown("---")

    # Chart Section
    pair = st.session_state.get("selected_pair", "EUR/USD")
    st.subheader("📈 Chart: " + pair)
    
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
            fig.add_trace(go.Scatter(x=df.index, y=df["sma_20"], name="SMA 20", line=dict(color="orange")))
            
        fig.update_layout(
            title=pair + " Overview", 
            height=400, 
            template="plotly_dark", 
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=40, b=10) # Hemat space di mobile
        )
        st.plotly_chart(fig, use_container_width=True)

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        change = ((latest["close"] - prev["close"]) / prev["close"]) * 100 if len(df) > 1 else 0

        # Price Info
        p1, p2, p3 = st.columns(3)
        with p1: st.metric("Current Price", f"{latest['close']:.5f}", f"{change:+.3f}%")
        with p2:
            rsi_val = latest.get("rsi_14", 50)
            st.metric("RSI (14)", f"{rsi_val:.1f}", "Oversold" if rsi_val < 30 else "Overbought" if rsi_val > 70 else "Neutral")
        with p3: st.metric("ATR (14)", f"{latest.get('atr_14', 0):.5f}", "Volatility")
    else:
        st.warning("⚠️ Gagal memuat data chart.")

    st.markdown("---")

    # Market Overview
    st.subheader("🌍 Market Overview")
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"]
    rows = []
    for p in pairs:
        d = fallback_to_frankfurter(p, days=2)
        if not d.empty and "close" in d.columns:
            cur = d.iloc[-1]["close"]
            prev = d.iloc[-2]["close"] if len(d) > 1 else cur
            chg = ((cur - prev) / prev) * 100
            rows.append({"Pair": p, "Price": f"{cur:.5f}", "Change": f"{chg:+.3f}%", 
                         "Trend": "🟢 Bullish" if chg > 0.1 else "🔴 Bearish" if chg < -0.1 else "⚪ Neutral"})

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

    # Navigation Buttons (2x2 grid, CSS otomatis bikin full-width di HP)
    n1, n2 = st.columns(2)
    with n1:
        if st.button("📊 Live Rates", use_container_width=True): st.switch_page("pages/2_Live_Rates.py")
        if st.button("📈 Technical Analysis", use_container_width=True): st.switch_page("pages/3_Technical_Analysis.py")
    with n2:
        if st.button("🚀 Trading Strategies", use_container_width=True): st.switch_page("pages/6_Trading_Strategies.py")
        if st.button("🤖 AI Scoring", use_container_width=True): st.switch_page("pages/7_AI_Analysis_Scoring.py")

    add_disclaimer()

if __name__ == "__main__":
    main()
