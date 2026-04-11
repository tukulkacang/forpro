import streamlit as st

st.set_page_config(page_title="ForPro Forex", layout="wide", initial_sidebar_state="expanded")

with st.sidebar:
    st.markdown("## ⚙️ Settings")

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
st.info("👈 Pilih pair dan halaman dari sidebar untuk memulai.")
