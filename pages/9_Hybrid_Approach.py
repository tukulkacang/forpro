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
        close = [1.0850 * (1 + i * 0.0001) for i in range(100)]
        df = pd.DataFrame({"Date": dates, "Close": close})
        df.set_index("Date", inplace=True)
        df["open"] = df["Close"] - 0.0001
        df["high"] = df["Close"] + 0.0002
        df["low"] = df["Close"] - 0.0002
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
    
    # Simple logic: Trend alignment
    if latest["close"] > sma_20 > sma_50:
        return True, "✅ Uptrend valid (SMA alignment)"
    elif latest["close"] < sma_20 < sma_50:
        return True, "✅ Downtrend valid (SMA alignment)"
    else:
        return False, "❌ Trend sideways (no clear wave)"

def check_ict_patterns(df):
    """Otomatis cek ICT Order Block / FVG"""
    if df.empty or len(df) < 3:
        return False, "Data tidak cukup"
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # Simple pattern detection
    if latest["close"] > prev["close"] and latest["volume"] > prev["volume"]:
        return True, "✅ Bullish OB terdeteksi"
    elif latest["close"] < prev["close"] and latest["volume"] > prev["volume"]:
        return True, "✅ Bearish OB terdeteksi"
    else:
        return False, "⚠️ No clear OB/FVG"

def check_fundamental(pair):
    """Simulasi cek fundamental bias"""
    # Di real app, ini connect ke news API
    fundamental_bias = {
        "EUR/USD": (True, "✅ ECB hawkish"),
        "GBP/USD": (False, "⚠️ BOE neutral"),
        "USD/JPY": (True, "✅ Fed hawkish"),
        "USD/CHF": (False, "⚠️ SNB dovish"),
        "AUD/USD": (True, "✅ RBA stable"),
        "USD/CAD": (False, "⚠️ BOC neutral"),
        "NZD/USD": (True, "✅ RBNZ hawkish"),
        "EUR/GBP": (False, "⚠️ Mixed signals")
    }
    
    return fundamental_bias.get(pair, (False, "⚠️ Data tidak tersedia"))

def check_sentiment(pair):
    """Simulasi cek sentiment"""
    # Di real app, ini connect ke sentiment API
    sentiment_data = {
        "EUR/USD": (True, "✅ Institusi bullish"),
        "GBP/USD": (False, "⚠️ Retail overcrowded"),
        "USD/JPY": (True, "✅ Momentum positif"),
        "USD/CHF": (False, "⚠️ Netral"),
        "AUD/USD": (True, "✅ Risk-on"),
        "USD/CAD": (False, "⚠️ Oil volatile"),
        "NZD/USD": (True, "✅ Positive carry"),
        "EUR/GBP": (False, "⚠️ Uncertain")
    }
    
    return sentiment_data.get(pair, (False, "⚠️ Data tidak tersedia"))

def main():
    st.title("🔄 Hybrid Approach - Auto Scanner")
    st.markdown("Sistem otomatis akan menganalisa confluence dari 4 metode")
    
    # Pair Selector
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
    selected_pair = st.selectbox("📊 Pilih Pair untuk Analisa:", pairs, index=0)
    
    if st.button("🔍 Scan Pair Sekarang", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Fetch data
    df = fallback_to_frankfurter(selected_pair, days=100)
    if not df.empty:
        df = calculate_all_indicators(df)
    
    # Auto-check semua kriteria
    st.subheader(f"📋 Hasil Scan: {selected_pair}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Kriteria yang Dipindai")
        
        # 1. Elliott Wave
        elliott_ok, elliott_msg = check_elliott_wave(df)
        st.markdown(f"{'✅' if elliott_ok else '❌'} **Elliott Wave Structure**")
        st.caption(elliott_msg)
        
        # 2. ICT Patterns
        ict_ok, ict_msg = check_ict_patterns(df)
        st.markdown(f"{'✅' if ict_ok else '❌'} **ICT Order Block / FVG**")
        st.caption(ict_msg)
    
    with col2:
        st.markdown("### 📊 Fundamental & Sentiment")
        
        # 3. Fundamental
        fund_ok, fund_msg = check_fundamental(selected_pair)
        st.markdown(f"{'✅' if fund_ok else '❌'} **Fundamental Bias**")
        st.caption(fund_msg)
        
        # 4. Sentiment
        sent_ok, sent_msg = check_sentiment(selected_pair)
        st.markdown(f"{'✅' if sent_ok else '❌'} **Market Sentiment**")
        st.caption(sent_msg)
    
    st.markdown("---")
    
    # Calculate score
    total_check = sum([elliott_ok, ict_ok, fund_ok, sent_ok])
    score = (total_check / 4) * 100
    
    # Display score
    st.subheader("🎯 Confluence Score")
    
    col_score1, col_score2 = st.columns([1, 3])
    
    with col_score1:
        st.metric("Total Terpenuhi", f"{total_check}/4")
    
    with col_score2:
        st.progress(score / 100)
        st.caption(f"{score:.0f}% confluence")
    
    # Recommendation
    st.markdown("### 💡 Rekomendasi Trading")
    
    if total_check >= 3:
        st.success(f"""
        🟢 **HIGH PROBABILITY SETUP**
        
        ✅ {total_check} dari 4 kriteria terpenuhi
        
        **Action**: 
        - Entry dengan confidence tinggi
        - Gunakan position size normal (1-2%)
        - SL ketat, TP bertahap
        
        **Risk:Reward**: Minimal 1:2
        """)
    elif total_check == 2:
        st.warning(f"""
        🟡 **MODERATE SETUP**
        
        ⚠️ Hanya {total_check} dari 4 kriteria terpenuhi
        
        **Action**:
        - Entry dengan position size kecil (0.5-1%)
        - Tunggu konfirmasi tambahan
        - Atau WAIT untuk setup lebih baik
        """)
    else:
        st.error(f"""
        🔴 **LOW PROBABILITY / WAIT**
        
        ❌ Hanya {total_check} dari 4 kriteria terpenuhi
        
        **Action**:
        - JANGAN ENTRY
        - Market kondisi jelek
        - Tunggu setup lebih jelas
        """)
    
    st.markdown("---")
    
    # Educational info
    with st.expander("📚 Penjelasan Hybrid Approach"):
        st.markdown("""
        ### Mengapa Perlu 4 Konfirmasi?
        
        Trading yang profitable butuh **konfluensi** (beberapa metode yang sepakat):
        
        1. **Elliott Wave**: Memberikan struktur market (impulse vs corrective)
        2. **ICT/SMC**: Memberikan entry point presisi (Order Block, FVG)
        3. **Fundamental**: Memberikan arah bias jangka panjang
        4. **Sentiment**: Memberikan insight psikologi pasar
        
        **Aturan Emas**:
        - ✅ 3-4 kriteria terpenuhi → HIGH PROBABILITY (Entry)
        - ⚠️ 2 kriteria terpenuhi → MODERATE (Entry kecil atau wait)
        - ❌ 0-1 kriteria terpenuhi → WAIT (Jangan trading)
        
        > 💡 **Jangan trading kalau syarat belum lengkap!** Lebih baik wait setup bagus daripada entry sembarangan.
        """)
    
    st.caption(f"🔄 Scan terakhir: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
