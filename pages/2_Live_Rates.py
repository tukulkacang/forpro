import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="📊 Live Rates", layout="wide")

@st.cache_data(ttl=300)
def get_rates():
    try:
        r = requests.get(
            "https://api.frankfurter.app/latest?base=USD&symbols=EUR,GBP,JPY,CHF,AUD,CAD,NZD",
            timeout=10
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def main():
    st.title("📊 Live Forex Rates")
    
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    data = get_rates()
    rates = data.get("rates", {})
    
    if not rates:
        st.error("❌ Gagal mengambil data. Periksa koneksi internet.")
        st.info("💡 Data dari Frankfurter API (ECB rates)")
        return
    
    # Major Pairs
    pairs = [
        ("EUR/USD", rates.get("EUR", 0)),
        ("GBP/USD", rates.get("GBP", 0)),
        ("USD/JPY", 1.0 / rates.get("JPY", 1) if rates.get("JPY") else 0),
        ("USD/CHF", 1.0 / rates.get("CHF", 1) if rates.get("CHF") else 0),
        ("AUD/USD", 1.0 / rates.get("AUD", 1) if rates.get("AUD") else 0),
        ("USD/CAD", 1.0 / rates.get("CAD", 1) if rates.get("CAD") else 0)
    ]
    
    rows = [{"Pair": p, "Rate": f"{r:.5f}", "Status": "✅ Active"} for p, r in pairs if r > 0]
    
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Tidak ada data tersedia.")
    
    st.markdown("---")
    
    # Currency Strength
    st.subheader("💪 Currency Strength (vs USD)")
    
    cols = st.columns(4)
    for i, (currency, rate) in enumerate(rates.items()):
        strength = ((rate - 1.0) / 1.0) * 100
        with cols[i % 4]:
            status = "Strong" if strength > 0 else "Weak"
            st.metric(currency, f"{strength:+.2f}%", status)
    
    st.caption(f"🔄 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB")

if __name__ == "__main__":
    main()