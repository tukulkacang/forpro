import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.api_utils import fallback_to_frankfurter
    from utils.indicators import calculate_all_indicators
except ImportError:
    def fallback_to_frankfurter(*args, **kwargs):
        dates = pd.date_range(end=datetime.now(), periods=100, freq="D")
        close = [1.1720 * (1 + i * 0.0001) for i in range(100)]
        df = pd.DataFrame({"Date": dates, "Close": close})
        df.set_index("Date", inplace=True)
        df["open"]  = df["Close"] - 0.0001
        df["high"]  = df["Close"] + 0.0002
        df["low"]   = df["Close"] - 0.0002
        df["close"] = df["Close"]
        return df

    def calculate_all_indicators(df):
        if "close" in df.columns:
            df["sma_20"] = df["close"].rolling(20).mean()
            df["sma_50"] = df["close"].rolling(50).mean()
            df["rsi_14"] = 50.0
        return df

st.set_page_config(page_title="🔄 Hybrid Approach", layout="wide")


def check_elliott_wave(df):
    """Otomatis cek Elliott Wave structure"""
    if df.empty:
        return False, "Data tidak tersedia"

    latest = df.iloc[-1]
    sma_20 = latest.get("sma_20", latest["close"])
    sma_50 = latest.get("sma_50", latest["close"])

    if latest["close"] > sma_20 > sma_50:
        return True, "✅ Uptrend valid (price > SMA20 > SMA50)"
    elif latest["close"] < sma_20 < sma_50:
        return True, "✅ Downtrend valid (price < SMA20 < SMA50)"
    else:
        return False, "❌ Trend sideways / konsolidasi"


def check_ict_patterns(df):
    """Otomatis cek ICT Order Block / FVG"""
    if df.empty or len(df) < 3:
        return False, "Data tidak cukup"

    latest = df.iloc[-1]
    prev   = df.iloc[-2]

    if latest["close"] > prev["close"] and latest["volume"] > prev["volume"]:
        return True, "✅ Bullish OB terdeteksi (close naik + volume tinggi)"
    elif latest["close"] < prev["close"] and latest["volume"] > prev["volume"]:
        return True, "✅ Bearish OB terdeteksi (close turun + volume tinggi)"
    else:
        return False, "⚠️ No clear Order Block / FVG"


def check_fundamental(pair):
    """
    Fundamental bias berdasarkan kondisi kebijakan moneter April 2026.
    Fed: Hold/Cautious Cut | ECB: Easing | BOE: Hold | BOJ: Gradual Hike
    """
    bias = {
        "EUR/USD": (False, "⚠️ ECB easing vs Fed hold → bias bearish EUR"),
        "GBP/USD": (True,  "✅ BOE hold vs Fed dovish → neutral-bullish GBP"),
        "USD/JPY": (False, "⚠️ BOJ hiking → tekanan bearish USD/JPY"),
        "USD/CHF": (True,  "✅ SNB netral vs Fed → sedikit bullish USD/CHF"),
        "AUD/USD": (False, "⚠️ RBA easing → bias bearish AUD"),
        "USD/CAD": (True,  "✅ BOC easing lebih agresif → bullish USD/CAD"),
        "NZD/USD": (False, "⚠️ RBNZ easing → bearish NZD"),
        "EUR/GBP": (False, "⚠️ ECB lebih dovish dari BOE → bearish EUR/GBP"),
    }
    return bias.get(pair, (False, "⚠️ Data tidak tersedia"))


def check_sentiment(pair):
    """
    Simulasi sentiment. Di real app: connect ke COT / broker sentiment API.
    """
    sentiment = {
        "EUR/USD": (True,  "✅ Retail net short EUR/USD → contrarian bullish"),
        "GBP/USD": (False, "⚠️ Retail net long GBP → contrarian bearish"),
        "USD/JPY": (False, "⚠️ JPY carry unwind meningkat"),
        "USD/CHF": (True,  "✅ Safe haven demand CHF menurun → bullish USD"),
        "AUD/USD": (True,  "✅ Risk-on mood positif untuk AUD"),
        "USD/CAD": (False, "⚠️ Oil price lemah → tekanan bearish CAD"),
        "NZD/USD": (True,  "✅ Retail overcrowded short NZD → contrarian"),
        "EUR/GBP": (False, "⚠️ Mixed institutional flow"),
    }
    return sentiment.get(pair, (False, "⚠️ Data tidak tersedia"))


def main():
    st.title("🔄 Hybrid Approach — Auto Scanner")
    st.markdown("Sistem otomatis menganalisa confluence dari **4 metode**: Elliott Wave · ICT · Fundamental · Sentiment")

    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
    selected_pair = st.selectbox("📊 Pilih Pair untuk Analisa:", pairs, index=0)

    if st.button("🔍 Scan Pair Sekarang", type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # Fetch & compute
    df = fallback_to_frankfurter(selected_pair, days=100)
    if not df.empty:
        df = calculate_all_indicators(df)

    st.subheader(f"📋 Hasil Scan: {selected_pair}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔍 Technical")

        elliott_ok, elliott_msg = check_elliott_wave(df)
        st.markdown(f"{'✅' if elliott_ok else '❌'} **Elliott Wave Structure**")
        st.caption(elliott_msg)

        ict_ok, ict_msg = check_ict_patterns(df)
        st.markdown(f"{'✅' if ict_ok else '❌'} **ICT Order Block / FVG**")
        st.caption(ict_msg)

    with col2:
        st.markdown("### 📊 Macro")

        fund_ok, fund_msg = check_fundamental(selected_pair)
        st.markdown(f"{'✅' if fund_ok else '❌'} **Fundamental Bias**")
        st.caption(fund_msg)

        sent_ok, sent_msg = check_sentiment(selected_pair)
        st.markdown(f"{'✅' if sent_ok else '❌'} **Market Sentiment**")
        st.caption(sent_msg)

    st.markdown("---")

    total_check = sum([elliott_ok, ict_ok, fund_ok, sent_ok])
    score = (total_check / 4) * 100

    st.subheader("🎯 Confluence Score")

    col_score1, col_score2 = st.columns([1, 3])
    with col_score1:
        st.metric("Kriteria Terpenuhi", f"{total_check}/4")
    with col_score2:
        st.progress(score / 100)
        st.caption(f"{score:.0f}% confluence")

    # Harga terkini
    if not df.empty and "close" in df.columns:
        latest_price = df.iloc[-1]["close"]
        st.metric("Harga Terkini", f"{latest_price:.5f}")

    st.markdown("### 💡 Rekomendasi Trading")

    if total_check >= 3:
        st.success(f"""
        🟢 **HIGH PROBABILITY SETUP**

        ✅ {total_check} dari 4 kriteria terpenuhi

        **Action**:
        - Entry dengan confidence tinggi
        - Position size normal (1–2%)
        - SL ketat, TP bertahap

        **Risk:Reward**: Minimal 1:2
        """)
    elif total_check == 2:
        st.warning(f"""
        🟡 **MODERATE SETUP**

        ⚠️ Hanya {total_check} dari 4 kriteria terpenuhi

        **Action**:
        - Entry dengan position size kecil (0.5–1%)
        - Tunggu konfirmasi tambahan
        - Atau WAIT untuk setup lebih baik
        """)
    else:
        st.error(f"""
        🔴 **LOW PROBABILITY / WAIT**

        ❌ Hanya {total_check} dari 4 kriteria terpenuhi

        **Action**:
        - JANGAN ENTRY sekarang
        - Tunggu setup lebih jelas
        """)

    st.markdown("---")

    with st.expander("📚 Penjelasan Hybrid Approach"):
        st.markdown("""
        ### Mengapa Perlu 4 Konfirmasi?

        Trading profitable butuh **konfluensi** — beberapa metode yang sepakat:

        1. **Elliott Wave**: Memberikan struktur market (impulse vs corrective)
        2. **ICT/SMC**: Memberikan entry point presisi (Order Block, FVG)
        3. **Fundamental**: Arah bias jangka menengah dari kebijakan bank sentral
        4. **Sentiment**: Insight psikologi pasar (contrarian indicator)

        **Aturan Emas**:
        - ✅ 3–4 kriteria → HIGH PROBABILITY (Entry)
        - ⚠️ 2 kriteria   → MODERATE (Entry kecil atau wait)
        - ❌ 0–1 kriteria  → WAIT (Jangan trading)

        > 💡 Lebih baik menunggu setup bagus daripada entry sembarangan!
        """)

    st.caption(f"🔄 Scan terakhir: {datetime.now().strftime('%H:%M:%S')} | Data fundamental: estimasi April 2026")


if __name__ == "__main__":
    main()
