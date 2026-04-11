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
        dates = pd.date_range(end=datetime.now(), periods=60, freq="D")
        close = [1.0850 * (1 + i * 0.0001) for i in range(60)]
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
            df["rsi_14"] = 50.0
        return df

st.set_page_config(page_title="🤖 AI Analysis Scoring", layout="wide")

def main():
    st.title("🤖 AI Analysis & Hybrid Scoring")
    
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    # Fetch data
    df = fallback_to_frankfurter(pair, days=60)
    
    if not df.empty and "close" in df.columns:
        df = calculate_all_indicators(df)
        
        # Calculate scores (simulated logic)
        rsi = df.iloc[-1]["rsi_14"] if "rsi_14" in df.columns else 50
        price = df.iloc[-1]["close"]
        sma = df.iloc[-1]["sma_20"] if "sma_20" in df.columns else price
        
        # Technical score
        tech_score = 50
        if rsi < 30:
            tech_score = 80
        elif rsi > 70:
            tech_score = 20
        elif 45 <= rsi <= 55:
            tech_score = 50
        else:
            tech_score = 60 if rsi < 50 else 40
        
        # Fundamental score (simulated)
        fund_score = 50
        
        # Sentiment score (simulated)
        sent_score = 50
        
        # Hybrid score
        hybrid_score = round(tech_score * 0.5 + fund_score * 0.3 + sent_score * 0.2, 1)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Technical", f"{tech_score}/100")
        col2.metric("Fundamental", f"{fund_score}/100")
        col3.metric("Sentiment", f"{sent_score}/100")
        col4.metric("Hybrid", f"{hybrid_score}/100")
        
        # Progress bars
        st.markdown("### 📈 Score Breakdown")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Technical Analysis**")
            st.progress(tech_score / 100)
            st.caption("Weight: 50%")
        with c2:
            st.markdown(f"**Fundamental Analysis**")
            st.progress(fund_score / 100)
            st.caption("Weight: 30%")
        with c3:
            st.markdown(f"**Market Sentiment**")
            st.progress(sent_score / 100)
            st.caption("Weight: 20%")
        
        st.markdown("---")
        
        # AI Insight
        st.subheader("💡 AI Insight (Bahasa Indonesia)")
        
        if hybrid_score >= 65:
            st.success(f"""
            🟢 **Sinyal KUAT BUY untuk {pair}**
            
            **Analisis**:
            - Technical & sentimen selaras bullish
            - Entry di pullback ke support
            - SL ketat di bawah recent low
            - TP bertahap dengan R:R 1:2
            
            **Action**: Pertimbangkan entry dengan risk management ketat
            """)
        elif hybrid_score <= 35:
            st.error(f"""
            🔴 **Sinyal KUAT SELL untuk {pair}**
            
            **Analisis**:
            - Bearish pressure dominan
            - Hindari counter-trend trades
            - Fokus short setup di rally
            - TP di Fib extension
            
            **Action**: Consider short positions dengan SL ketat
            """)
        elif 50 <= hybrid_score < 65:
            st.info(f"""
            🟡 **Sinyal MODERATE BUY untuk {pair}**
            
            **Analisis**:
            - Bias bullish tapi perlu konfirmasi tambahan
            - Tunggu pullback lebih dalam
            - Gunakan position size lebih kecil
            
            **Action**: Entry dengan position size 0.5-1%
            """)
        else:
            st.warning(f"""
            ⚪ **NEUTRAL / WAIT untuk {pair}**
            
            **Analisis**:
            - Market sideways / no clear edge
            - Low confluence
            - Tidak ada setup high probability
            
            **Action**: WAIT untuk setup lebih baik
            """)
        
        st.info("""
        💡 **Hybrid Score Methodology**:
        
        Hybrid Score = Technical(50%) + Fundamental(30%) + Sentiment(20%)
        
        - **70-100**: Strong Buy/Sell signal
        - **55-69**: Moderate Buy/Sell signal
        - **45-54**: Neutral/Wait
        - **30-44**: Weak Sell/Buy signal
        - **0-29**: Strong Sell/Buy signal
        
        Gunakan sebagai **filter probabilitas**, bukan sinyal entry otomatis.
        Selalu konfirmasi dengan price action dan risk management.
        """)
    
    else:
        st.warning("⚠️ Gagal memuat data untuk scoring.")

if __name__ == "__main__":
    main()