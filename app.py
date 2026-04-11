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

# =============================================================================
# AUTO-LOAD API KEY FROM STREAMLIT SECRETS (PENTING!)
# =============================================================================
# Cek apakah API key ada di secrets.toml atau Streamlit Cloud Settings
if "TWELVE_DATA_API_KEY" in st.secrets:
    st.session_state.twelve_api_key = st.secrets["TWELVE_DATA_API_KEY"]
    st.session_state.data_source = "Twelve Data"  # Auto-set ke Twelve Data jika key ada

with st.sidebar:
    st.title("📊 Forex Analysis Pro")
    st.caption("Dashboard Analisa & Strategi Forex 2026")
    st.markdown("---")
    
    # Data Source Selection
    st.subheader("🔌 Data Source")
    
    # Cek apakah API key tersedia (dari secrets atau manual)
    has_api_key = bool(st.session_state.twelve_api_key)
    
    source_options = ["Frankfurter (Gratis)", "Twelve Data (Advanced)"]
    
    # Set default index berdasarkan availability
    default_idx = 1 if (has_api_key and st.session_state.data_source == "Twelve Data") else 0
    
    source_selection = st.selectbox(
        "Pilih API:",
        source_options,
        index=default_idx,
        disabled=not has_api_key  # Disable jika tidak ada API key
    )
    
    if "Twelve Data" in source_selection:
        st.session_state.data_source = "Twelve Data"
        
        # Tampilkan status API key (tanpa input field jika sudah ada di secrets)
        if has_api_key:
            key_preview = st.session_state.twelve_api_key[:8] + "..." + st.session_state.twelve_api_key[-4:]
            st.success(f"✅ Twelve Data API: **{key_preview}**")
            st.caption("🔑 API key loaded from secrets.toml")
        else:
            # Fallback: input manual jika tidak ada di secrets
            st.warning("⚠️ API key tidak ditemukan di secrets")
            api_key_input = st.text_input(
                "🔑 Twelve Data API Key",
                value=st.session_state.twelve_api_key,
                type="password",
                help="Atau tambahkan di .streamlit/secrets.toml"
            )
            st.session_state.twelve_api_key = api_key_input
            if api_key_input:
                st.info("ℹ️ API key tersimpan di session (temporary)")
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

# Show API source badge
if st.session_state.data_source == "Twelve Data" and st.session_state.twelve_api_key:
    st.markdown("🔌 **Data Source:** Twelve Data API (Real-time) 🔵")
else:
    st.markdown("🔌 **Data Source:** Frankfurter API (Daily) 🟢")

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
