import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="📉 Fundamental Analysis", layout="wide")

def main():
    st.title("📉 Fundamental Analysis")
    
    # Central Banks Rates
    st.header("🏦 Central Bank Interest Rates & Policy")
    
    banks_df = pd.DataFrame({
        "Bank": [
            "Federal Reserve (USD)",
            "ECB (EUR)",
            "Bank of England (GBP)",
            "Bank of Japan (JPY)",
            "RBA (AUD)",
            "SNB (CHF)"
        ],
        "Rate (%)": [5.50, 4.50, 5.25, -0.10, 4.35, 1.75],
        "Bias": ["Hawkish", "Neutral", "Hold", "Dovish", "Hold", "Neutral"],
        "Next Meeting": [
            (datetime.now() + timedelta(days=12)).strftime("%b %d"),
            (datetime.now() + timedelta(days=6)).strftime("%b %d"),
            (datetime.now() + timedelta(days=20)).strftime("%b %d"),
            (datetime.now() + timedelta(days=14)).strftime("%b %d"),
            (datetime.now() + timedelta(days=11)).strftime("%b %d"),
            (datetime.now() + timedelta(days=25)).strftime("%b %d")
        ]
    })
    
    st.dataframe(banks_df, use_container_width=True, hide_index=True)
    st.caption("⚠️ Data suku bunga bersifat simulasi untuk tujuan edukasi.")
    
    st.markdown("---")
    
    # Interest Rate Differential Calculator
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
    
    # Interest rates mapping
    rates_map = {
        "USD": 5.50,
        "EUR": 4.50,
        "GBP": 5.25,
        "JPY": -0.10,
        "AUD": 4.35,
        "CAD": 5.00,
        "CHF": 1.75,
        "NZD": 5.50
    }
    
    if base_curr != quote_curr:
        base_rate = rates_map[base_curr]
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
            st.info("⚪ Neutral - Tidak ada differential")
    
    st.markdown("---")
    
    # Economic Calendar
    st.header("📅 Economic Calendar (Upcoming High Impact Events)")
    
    calendar_df = pd.DataFrame([
        {
            "Date": "Today",
            "Time": "14:30",
            "Currency": "USD",
            "Event": "Non-Farm Payrolls",
            "Impact": "🔴 HIGH",
            "Forecast": "185K",
            "Previous": "150K"
        },
        {
            "Date": "Today",
            "Time": "14:30",
            "Currency": "USD",
            "Event": "Unemployment Rate",
            "Impact": "🔴 HIGH",
            "Forecast": "3.8%",
            "Previous": "3.9%"
        },
        {
            "Date": "Tomorrow",
            "Time": "10:00",
            "Currency": "EUR",
            "Event": "ECB Interest Rate Decision",
            "Impact": "🔴 HIGH",
            "Forecast": "4.50%",
            "Previous": "4.50%"
        },
        {
            "Date": "+2 Days",
            "Time": "09:00",
            "Currency": "GBP",
            "Event": "GDP Growth Rate",
            "Impact": "🟡 MEDIUM",
            "Forecast": "0.2%",
            "Previous": "0.1%"
        },
        {
            "Date": "+3 Days",
            "Time": "22:30",
            "Currency": "JPY",
            "Event": "CPI y/y",
            "Impact": "🔴 HIGH",
            "Forecast": "2.8%",
            "Previous": "3.0%"
        },
        {
            "Date": "+4 Days",
            "Time": "14:30",
            "Currency": "USD",
            "Event": "Core PCE Price Index",
            "Impact": "🔴 HIGH",
            "Forecast": "2.8%",
            "Previous": "2.9%"
        }
    ])
    
    st.dataframe(calendar_df, use_container_width=True, hide_index=True)
    
    st.info("""
    💡 **Trading Tips Around News Events**:
    
    - Hindari trading **15 menit sebelum** dan **sesudah** rilis berita HIGH IMPACT
    - Volatilitas ekstrem dapat menyebabkan slippage dan spread melebar
    - Gunakan position size lebih kecil (50% dari normal) saat trading news
    - Pertimbangkan untuk close position sebelum news penting
    """)
    
    st.markdown("---")
    
    # Fundamental Bias
    st.header("📊 Fundamental Bias by Currency")
    
    bias_data = {
        "Currency": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"],
        "Economic Outlook": ["Strong", "Mixed", "Moderate", "Weak", "Stable", "Moderate", "Stable", "Strong"],
        "Monetary Policy": ["Hawkish", "Neutral", "Hold", "Dovish", "Hold", "Neutral", "Neutral", "Hawkish"],
        "Overall Bias": ["🟢 Bullish", "🟡 Neutral", "🟡 Neutral", "🔴 Bearish", "🟡 Neutral", "🟡 Neutral", "🟡 Neutral", "🟢 Bullish"]
    }
    
    st.dataframe(pd.DataFrame(bias_data), use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()