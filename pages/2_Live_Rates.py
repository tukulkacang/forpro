import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="📊 Live Rates", layout="wide")

@st.cache_data(ttl=60)
def get_rates():
    """
    Frankfurter base=USD mengembalikan: berapa unit currency per 1 USD
      rates["EUR"] = EUR per 1 USD  -> EUR/USD = 1 / rates["EUR"]
      rates["JPY"] = JPY per 1 USD  -> USD/JPY = rates["JPY"]  (langsung)
      rates["CHF"] = CHF per 1 USD  -> USD/CHF = rates["CHF"]  (langsung)
      rates["AUD"] = AUD per 1 USD  -> AUD/USD = 1 / rates["AUD"]
      rates["CAD"] = CAD per 1 USD  -> USD/CAD = rates["CAD"]  (langsung)
      rates["GBP"] = GBP per 1 USD  -> GBP/USD = 1 / rates["GBP"]
    """
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
    st.caption("Sumber: Frankfurter API (ECB Reference Rates) — Update setiap 60 detik")

    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    data  = get_rates()
    rates = data.get("rates", {})
    date  = data.get("date", "N/A")

    if not rates:
        st.error("❌ Gagal mengambil data. Periksa koneksi internet.")
        return

    # ── Major Pairs (konversi benar) ──────────────────────────────────────
    def safe_div(numerator, key, invert=False):
        val = rates.get(key)
        if not val:
            return 0.0
        return (1.0 / val) if invert else val

    pairs = [
        # (label,       nilai,                             arah konversi)
        ("EUR/USD",  safe_div(1, "EUR", invert=True)),   # 1/EUR_per_USD
        ("GBP/USD",  safe_div(1, "GBP", invert=True)),   # 1/GBP_per_USD
        ("USD/JPY",  safe_div(1, "JPY", invert=False)),   # JPY per USD = USD/JPY
        ("USD/CHF",  safe_div(1, "CHF", invert=False)),   # CHF per USD = USD/CHF
        ("AUD/USD",  safe_div(1, "AUD", invert=True)),    # 1/AUD_per_USD
        ("USD/CAD",  safe_div(1, "CAD", invert=False)),   # CAD per USD = USD/CAD
        ("NZD/USD",  safe_div(1, "NZD", invert=True)),    # 1/NZD_per_USD
    ]

    rows = [
        {"Pair": p, "Rate": f"{r:.5f}", "Status": "✅ Live"}
        for p, r in pairs if r > 0
    ]

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Tidak ada data tersedia.")

    st.markdown("---")

    # ── Currency Strength (vs USD) ────────────────────────────────────────
    st.subheader("💪 Currency Strength (vs USD)")
    st.caption("Positif = currency lebih kuat dari nilai referensi 1:1 vs USD")

    cols = st.columns(4)
    strength_pairs = [
        ("EUR", safe_div(1, "EUR", invert=True)),
        ("GBP", safe_div(1, "GBP", invert=True)),
        ("JPY", safe_div(1, "JPY", invert=False)),
        ("CHF", safe_div(1, "CHF", invert=False)),
        ("AUD", safe_div(1, "AUD", invert=True)),
        ("CAD", safe_div(1, "CAD", invert=False)),
        ("NZD", safe_div(1, "NZD", invert=True)),
    ]

    # Strength dihitung relatif: berapa % harga pair bergerak dari angka 1.0
    for i, (currency, price) in enumerate(strength_pairs):
        with cols[i % 4]:
            delta_pct = ((price - 1.0) / 1.0) * 100
            st.metric(
                label=currency,
                value=f"{price:.4f}",
                delta=f"{delta_pct:+.2f}%"
            )

    st.markdown("---")
    st.caption(f"📅 ECB Rate Date: {date} | 🔄 Last Fetch: {datetime.now().strftime('%H:%M:%S')} WIB")


if __name__ == "__main__":
    main()
