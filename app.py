import streamlit as st

st.set_page_config(page_title="ForPro Forex", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.subheader("🔑 Twelve Data API Key")
    key_input = st.text_input(
        "API Key",
        type="password",
        value=st.session_state.get("twelve_api_key", ""),
        help="Dapatkan gratis di twelvedata.com"
    )
    if key_input:
        st.session_state["twelve_api_key"] = key_input
        st.success("✅ API Key tersimpan")
    else:
        st.warning("⚠️ Masukkan API Key dulu")

    st.markdown("---")
    st.subheader("📊 Selected Pair")
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
    selected = st.selectbox(
        "Pair",
        pairs,
        index=pairs.index(st.session_state.get("selected_pair", "EUR/USD"))
    )
    st.session_state["selected_pair"] = selected

    st.markdown("---")
    st.subheader("💰 Account Settings")
    balance = st.number_input("Balance ($)", value=st.session_state.get("account_balance", 10000), min_value=100)
    risk    = st.slider("Risk per Trade (%)", 0.5, 5.0, st.session_state.get("risk_per_trade", 1.0), 0.5)
    st.session_state["account_balance"] = balance
    st.session_state["risk_per_trade"]  = risk

st.title("🏠 ForPro Forex Dashboard")
st.info("👈 Set API Key di sidebar, lalu pilih halaman dari menu navigasi.")
