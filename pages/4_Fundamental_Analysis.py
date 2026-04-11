import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="📉 Fundamental Analysis", layout="wide")

def main():
    st.title("📉 Fundamental Analysis")

    # ── Central Bank Interest Rates (Update April 2026) ───────────────────
    st.header("🏦 Central Bank Interest Rates & Policy")
    st.caption("⚠️ Referensi estimasi April 2026 — selalu cek situs resmi bank sentral untuk data terkini")

    banks_df = pd.DataFrame({
        "Bank": [
            "Federal Reserve (USD)",
            "ECB (EUR)",
            "Bank of England (GBP)",
            "Bank of Japan (JPY)",
            "RBA (AUD)",
            "SNB (CHF)",
            "Bank of Canada (CAD)",
            "RBNZ (NZD)",
        ],
        "Rate (%)": [4.25, 2.40, 4.50, 0.50, 4.10, 0.25, 2.75, 3.50],
        "Bias": [
            "Hold / Cautious Cut",
            "Easing",
            "Hold",
            "Gradual Hike",
            "Hold / Easing",
            "Neutral",
            "Easing",
            "Easing",
        ],
        "Next Meeting": [
            (datetime.now() + timedelta(days=18)).strftime("%b %d"),
            (datetime.now() + timedelta(days=10)).strftime("%b %d"),
            (datetime.now() + timedelta(days=22)).strftime("%b %d"),
            (datetime.now() + timedelta(days=14)).strftime("%b %d"),
            (datetime.now() + timedelta(days=5)).strftime("%b %d"),
            (datetime.now() + timedelta(days=30)).strftime("%b %d"),
            (datetime.now() + timedelta(days=12)).strftime("%b %d"),
            (datetime.now() + timedelta(days=25)).strftime("%b %d"),
        ],
    })

    st.dataframe(banks_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # ── Carry Trade Calculator ─────────────────────────────────────────────
    st.header("💱 Interest Rate Differential Calculator (Carry Trade)")

    col1, col2 = st.columns(2)
    with col1:
        base_curr = st.selectbox(
            "Base Currency (Buy)",
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]
        )
    with col2:
        quote_curr = st.selectbox(
            "Quote Currency (Sell)",
            ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"],
            index=1
        )

    rates_map = {
        "USD": 4.25,
        "EUR": 2.40,
        "GBP": 4.50,
        "JPY": 0.50,
        "AUD": 4.10,
        "CAD": 2.75,
        "CHF": 0.25,
        "NZD": 3.50,
    }

    if base_curr != quote_curr:
        base_rate  = rates_map[base_curr]
        quote_rate = rates_map[quote_curr]
        differential = base_rate - quote_rate

        st.metric(
            f"{base_curr}/{quote_curr} Interest Rate Differential",
            f"{differential:+.2f}%"
        )

        if differential > 0:
            st.success(f"""
            ✅ **Positive Carry Trade**

            - Anda berpotensi mendapatkan **swap positif** pada posisi BUY {base_curr}/{quote_curr}
            - Annual carry: +{differential:.2f}%
            - Cocok untuk position trading jangka panjang
            """)
        elif differential < 0:
            st.warning(f"""
            ⚠️ **Negative Carry Trade**

            - Anda akan dikenakan **biaya swap** pada posisi BUY {base_curr}/{quote_curr}
            - Annual cost: {differential:.2f}%
            - Pertimbangkan posisi SELL untuk positive carry
            """)
        else:
            st.info("⚪ Neutral — tidak ada differential")

    st.markdown("---")

    # ── Economic Calendar ─────────────────────────────────────────────────
    st.header("📅 Economic Calendar (High Impact Events)")
    st.caption("Data bersifat ilustrasi — gunakan Forex Factory / Investing.com untuk kalender real-time")

    calendar_df = pd.DataFrame([
        {
            "Date": "Today",
            "Time": "14:30",
            "Currency": "USD",
            "Event": "Core CPI m/m",
            "Impact": "🔴 HIGH",
            "Forecast": "0.3%",
            "Previous": "0.2%",
        },
        {
            "Date": "Today",
            "Time": "20:00",
            "Currency": "USD",
            "Event": "FOMC Minutes",
            "Impact": "🔴 HIGH",
            "Forecast": "-",
            "Previous": "-",
        },
        {
            "Date": "Tomorrow",
            "Time": "09:30",
            "Currency": "GBP",
            "Event": "CPI y/y",
            "Impact": "🔴 HIGH",
            "Forecast": "2.6%",
            "Previous": "2.8%",
        },
        {
            "Date": "+2 Days",
            "Time": "11:45",
            "Currency": "EUR",
            "Event": "ECB Rate Decision",
            "Impact": "🔴 HIGH",
            "Forecast": "2.40%",
            "Previous": "2.65%",
        },
        {
            "Date": "+3 Days",
            "Time": "01:30",
            "Currency": "AUD",
            "Event": "Employment Change",
            "Impact": "🟡 MEDIUM",
            "Forecast": "25K",
            "Previous": "32K",
        },
        {
            "Date": "+4 Days",
            "Time": "14:30",
            "Currency": "USD",
            "Event": "Non-Farm Payrolls",
            "Impact": "🔴 HIGH",
            "Forecast": "155K",
            "Previous": "143K",
        },
    ])

    st.dataframe(calendar_df, use_container_width=True, hide_index=True)

    st.info("""
    💡 **Tips Trading Sekitar News Events**:

    - Hindari trading **15 menit sebelum** dan **sesudah** rilis berita HIGH IMPACT
    - Volatilitas ekstrem dapat menyebabkan slippage dan spread melebar
    - Gunakan position size lebih kecil (50% dari normal) saat trading news
    - Pertimbangkan close posisi sebelum news penting
    """)

    st.markdown("---")

    # ── Fundamental Bias ──────────────────────────────────────────────────
    st.header("📊 Fundamental Bias by Currency (April 2026)")
    st.caption("Estimasi bias berdasarkan kondisi kebijakan moneter terkini")

    bias_data = {
        "Currency": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"],
        "Economic Outlook": [
            "Resilient",
            "Recovering",
            "Stable",
            "Improving",
            "Mixed",
            "Softening",
            "Stable",
            "Weakening",
        ],
        "Monetary Policy": [
            "Hold / Cautious Cut",
            "Easing",
            "Hold",
            "Gradual Hike",
            "Hold / Easing",
            "Easing",
            "Neutral",
            "Easing",
        ],
        "Overall Bias": [
            "🟡 Neutral-Bullish",
            "🟡 Neutral",
            "🟡 Neutral",
            "🟢 Bullish (vs carry)",
            "🟡 Neutral",
            "🔴 Bearish",
            "🟡 Neutral",
            "🔴 Bearish",
        ],
    }

    st.dataframe(pd.DataFrame(bias_data), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
