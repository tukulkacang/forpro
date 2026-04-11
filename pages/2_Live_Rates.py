import streamlit as st
import pandas as pd
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api_utils import get_live_rate, fetch_twelve_data

st.set_page_config(page_title="📊 Live Rates", layout="wide")

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]

def main():
    st.title("📊 Live Forex Rates")
    st.caption("Sumber: Twelve Data API — real-time")

    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # Live prices
    rows = []
    for pair in PAIRS:
        price, err = get_live_rate(pair)
        if price:
            rows.append({"Pair": pair, "Rate": f"{price:.5f}", "Status": "✅ Live"})
        else:
            rows.append({"Pair": pair, "Rate": "—", "Status": f"⚠️ {err}"})

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Daily change
    st.subheader("📈 Daily Change")
    change_rows = []
    for pair in PAIRS:
        df, err = fetch_twelve_data(pair, interval="1day", outputsize=2)
        if df is not None and len(df) >= 2:
            cur  = df.iloc[-1]["close"]
            prev = df.iloc[-2]["close"]
            chg  = ((cur - prev) / prev) * 100
            change_rows.append({
                "Pair":   pair,
                "Close":  f"{cur:.5f}",
                "Change": f"{chg:+.3f}%",
                "Trend":  "🟢 Bullish" if chg > 0.05 else "🔴 Bearish" if chg < -0.05 else "⚪ Flat",
            })
        else:
            change_rows.append({"Pair": pair, "Close": "—", "Change": "—", "Trend": f"⚠️ {err}"})

    st.dataframe(pd.DataFrame(change_rows), use_container_width=True, hide_index=True)
    st.caption(f"🔄 Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
