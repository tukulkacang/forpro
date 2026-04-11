import streamlit as st
from datetime import datetime

# Page config
st.set_page_config(
    page_title="📊 Forex Analysis Pro 2026",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "selected_pair" not in st.session_state:
    st.session_state.selected_pair = "EUR/USD"
if "timeframe" not in st.session_state:
    st.session_state.timeframe = "1day"
if "data_source" not in st.session_state:
    st.session_state.data_source = "Frankfurter"
if "twelve_api_key" not in st.session_state:
    st.session_state.twelve_api_key = ""
if "account_balance" not in st.session_state:
    st.session_state.account_balance = 10000.0
if "risk_per_trade" not in st.session_state:
    st.session_state.risk_per_trade = 1.0

# Sidebar
with st.sidebar:
    st.title("📊 Forex Analysis Pro")
    st.caption("Dashboard Analisa & Strategi Forex 2026")
    st.markdown("---")
    
    # Data Source
    st.subheader("🔌 Data Source")
    source_options = ["Frankfurter (Gratis)", "Twelve Data (Advanced)"]
    default_idx = 0 if st.session_state.data_source == "Frankfurter" else 1
    
    source_selection = st.selectbox(
        "Pilih API:",
        source_options,
        index=default_idx
    )
    
    if "Twelve Data" in source_selection:
        st.session_state.data_source = "Twelve Data"
        api_key = st.text_input(
            "🔑 Twelve Data API Key",
            value=st.session_state.twelve_api_key,
            type="password"
        )
        st.session_state.twelve_api_key = api_key
        if api_key:
            st.success("✅ API Key tersimpan")
    else:
        st.session_state.data_source = "Frankfurter"
        st.info("ℹ️ Menggunakan Frankfurter API (Daily Data)")
    
    st.markdown("---")
    
    # Pair Selection
    st.subheader("💱 Pair & Timeframe")
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
    current_idx = pairs.index(st.session_state.selected_pair) if st.session_state.selected_pair in pairs else 0
    
    st.session_state.selected_pair = st.selectbox(
        "Pilih Pair:",
        pairs,
        index=current_idx
    )
    
    # Timeframe Selection
    timeframes = ["1min", "5min", "15min", "30min", "1h", "4h", "1day"]
    current_tf_idx = timeframes.index(st.session_state.timeframe) if st.session_state.timeframe in timeframes else 6
    
    st.session_state.timeframe = st.selectbox(
        "Interval:",
        timeframes,
        index=current_tf_idx
    )
    
    st.markdown("---")
    st.caption(f"🔄 Last Update: {datetime.now().strftime('%H:%M:%S')}")

# Main Content
st.markdown('<h1 style="text-align:center;">🚀 Forex Analysis Pro 2026</h1>', unsafe_allow_html=True)
st.markdown(f"**Pair Aktif:** `{st.session_state.selected_pair}` | **Timeframe:** `{st.session_state.timeframe}`")
st.markdown("---")

# Navigation Buttons
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/1_Home.py")

with c2:
    if st.button("📊 Live Rates", use_container_width=True):
        st.switch_page("pages/2_Live_Rates.py")

with c3:
    if st.button("📈 Technical", use_container_width=True):
        st.switch_page("pages/3_Technical_Analysis.py")

with c4:
    if st.button("🚀 Strategies", use_container_width=True):
        st.switch_page("pages/6_Trading_Strategies.py")

st.markdown("---")

# Welcome Content
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🎯 Selamat Datang di Forex Analysis Pro!")
    st.markdown("""
    Aplikasi ini menyediakan **analisa forex lengkap** dengan pendekatan hybrid:
    
    🔹 **Teknikal**: 100+ indikator, pattern detection, multi-timeframe  
    🔹 **Fundamental**: Economic calendar, suku bunga bank sentral  
    🔹 **Sentimen**: COT report, retail positioning, fear & greed index  
    🔹 **Strategi**: Elliott Wave + ICT, Scalping, Day Trading, Swing Trading  
    🔹 **AI Scoring**: Hybrid score 0-100 dengan insight Bahasa Indonesia  
    🔹 **Risk Management**: Position sizing calculator, Entry/SL/TP recommendation  
    
    💡 **Tips**: Gunakan sidebar untuk mengubah Pair, Timeframe, atau Data Source.
    """)

with col_right:
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔍 AI Scoring", use_container_width=True):
        st.switch_page("pages/7_AI_Analysis_Scoring.py")
    
    if st.button("🎯 Entry Recommendation", use_container_width=True):
        st.switch_page("pages/8_Trading_Recommendation.py")
    
    if st.button("🔄 Hybrid Approach", use_container_width=True):
        st.switch_page("pages/9_Hybrid_Approach.py")
    
    if st.button("⭐ Watchlist", use_container_width=True):
        st.switch_page("pages/10_Watchlist.py")

# Disclaimer
from utils.helpers import add_disclaimer
add_disclaimer()