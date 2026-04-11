import streamlit as st
from datetime import datetime

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="📊 Forex Analysis Pro 2026",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed" # Default collapsed di mobile biar lega
)

# =============================================================================
# MOBILE RESPONSIVE CSS
# =============================================================================
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stColumns > div { width: 100% !important; display: block !important; margin-bottom: 1rem !important; }
        .stButton > button { width: 100% !important; margin-bottom: 0.5rem !important; }
        div[data-testid="stMetric"] { margin-bottom: 0.5rem !important; }
        .main-header { font-size: 1.8rem !important; }
    }
    .main-header { text-align: center; font-size: 2.2rem; font-weight: bold; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# STATE INITIALIZATION
# =============================================================================
if "selected_pair" not in st.session_state: st.session_state.selected_pair = "EUR/USD"
if "timeframe" not in st.session_state: st.session_state.timeframe = "1day"
if "data_source" not in st.session_state: st.session_state.data_source = "Twelve Data"
if "twelve_api_key" not in st.session_state: st.session_state.twelve_api_key = ""
if "account_balance" not in st.session_state: st.session_state.account_balance = 10000.0
if "risk_per_trade" not in st.session_state: st.session_state.risk_per_trade = 1.0

# =============================================================================
# SIDEBAR (UPDATED: OTOMATIS & RAPI)
# =============================================================================
with st.sidebar:
    st.title("📊 Forex Pro")
    st.caption("Dashboard Analisa & Strategi")
    st.markdown("---")
    
    # 1. DATA SOURCE LOGIC (SIMPLIFIED)
    st.subheader("🔌 Data Source")
    
    # Cek apakah ada API Key di Secrets ATAU di Session State
    has_key = "TWELVE_DATA_API_KEY" in st.secrets or bool(st.session_state.twelve_api_key)
    
    if has_key:
        st.success("✅ **Twelve Data Active**")
        st.caption("Harga Real-time (Mirip MT5)")
        st.session_state.data_source = "Twelve Data"
    else:
        st.warning("⚠️ API Key Belum Terdeteksi")
        st.caption("Sistem pakai data simulasi sementara.")
        
        # Input manual jika belum ada key
        api_key_input = st.text_input("Masukkan Twelve Data Key", type="password")
        if api_key_input:
            st.session_state.twelve_api_key = api_key_input
            st.success("Key tersimpan sementara!")
            st.session_state.data_source = "Twelve Data"

    st.markdown("---")
    
    # 2. PAIR & TIMEFRAME
    st.subheader("💱 Pair & TF")
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
    idx = pairs.index(st.session_state.selected_pair) if st.session_state.selected_pair in pairs else 0
    
    st.session_state.selected_pair = st.selectbox("Pair", pairs, index=idx)
    
    tfs = ["1min", "5min", "15min", "30min", "1h", "4h", "1day"]
    tidx = tfs.index(st.session_state.timeframe) if st.session_state.timeframe in tfs else 6
    st.session_state.timeframe = st.selectbox("Timeframe", tfs, index=tidx)
    
    st.markdown("---")
    st.caption(f"🔄 {datetime.now().strftime('%H:%M:%S')}")

# =============================================================================
# MAIN CONTENT
# =============================================================================
st.markdown('<p class="main-header">🚀 Forex Analysis Pro 2026</p>', unsafe_allow_html=True)

# Badge Status Data Source
if has_key:
    st.success("🟢 **Mode: Real-time Data** (Twelve Data API)")
else:
    st.info("🟡 **Mode: Simulasi** (API Key belum diisi)")

st.markdown(f"**Pair Aktif:** `{st.session_state.selected_pair}` | **TF:** `{st.session_state.timeframe}`")
st.markdown("---")

# NAVIGATION BUTTONS (RESPONSIVE)
c1, c2 = st.columns(2)
with c1:
    if st.button("🏠 Home", use_container_width=True): st.switch_page("pages/1_Home.py")
    if st.button("📊 Live Rates", use_container_width=True): st.switch_page("pages/2_Live_Rates.py")
    if st.button("📈 Technical", use_container_width=True): st.switch_page("pages/3_Technical_Analysis.py")
with c2:
    if st.button("🚀 Strategies", use_container_width=True): st.switch_page("pages/6_Trading_Strategies.py")
    if st.button("🎯 Recommendation", use_container_width=True): st.switch_page("pages/8_Trading_Recommendation.py")
    if st.button("🤖 AI Scoring", use_container_width=True): st.switch_page("pages/7_AI_Analysis_Scoring.py")

st.markdown("---")

# Disclaimer
st.warning("⚠️ **Disclaimer**: Aplikasi ini untuk edukasi. Gunakan risk management ketat.")
