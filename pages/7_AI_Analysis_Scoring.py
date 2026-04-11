import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Groq Library
try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

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
    
    # Fetch Data
    df = fallback_to_frankfurter(pair, days=60)
    
    # Calculate Technical Scores (Simulated Logic)
    tech_score = 50
    rsi = 50
    
    if not df.empty and "close" in df.columns:
        df = calculate_all_indicators(df)
        rsi = df.iloc[-1]["rsi_14"]
        price = df.iloc[-1]["close"]
        sma = df.iloc[-1]["sma_20"]
        
        if rsi < 30: tech_score = 80
        elif rsi > 70: tech_score = 20
        elif price > sma: tech_score = 60
        else: tech_score = 40

    fund_score = 50
    sent_score = 50
    hybrid_score = round(tech_score * 0.5 + fund_score * 0.3 + sent_score * 0.2, 1)

    # Display Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Technical", f"{tech_score}/100")
    col2.metric("Fundamental", f"{fund_score}/100")
    col3.metric("Sentiment", f"{sent_score}/100")
    col4.metric("Hybrid", f"{hybrid_score}/100")
    
    st.markdown("### 📈 Score Breakdown")
    c1, c2, c3 = st.columns(3)
    with c1: st.progress(tech_score/100); st.caption("Weight: 50%")
    with c2: st.progress(fund_score/100); st.caption("Weight: 30%")
    with c3: st.progress(sent_score/100); st.caption("Weight: 20%")

    st.markdown("---")
    st.subheader("💡 AI Insight (Powered by Groq)")

    # --- GROQ INTEGRATION ---
    # Cek apakah Groq API Key ada di Streamlit Secrets
    if HAS_GROQ and "GROQ_API_KEY" in st.secrets:
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            # Prepare Context for AI
            context_text = f"""
            Pair: {pair}
            RSI (14): {rsi:.2f}
            Hybrid Score: {hybrid_score}
            Technical Score: {tech_score}
            Fundamental Score: {fund_score}
            Sentiment Score: {sent_score}
            """
            
            with st.spinner("🤖 AI sedang menganalisa data market..."):
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are a professional forex trading assistant. Provide concise, actionable trading insights in Indonesian based on the data provided."},
                        {"role": "user", "content": f"Berdasarkan data teknikal berikut untuk {pair}:\n{context_text}\nBerikan analisa singkat, sinyal utama (Buy/Sell/Wait), dan saran Risk Management."}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                
                insight = completion.choices[0].message.content
                st.markdown(insight)
                st.success("✅ Analisis berhasil dibuat oleh Groq AI.")

        except Exception as e:
            st.error(f"❌ Error Groq: {e}")
            st.info("💡 Fallback ke insight standar.")
            st.info(f"💡 **Sinyal: {'BUY' if hybrid_score > 50 else 'SELL'}**. Gunakan risk management ketat.")

    # --- FALLBACK IF NO GROQ ---
    else:
        if hybrid_score >= 65:
            st.success(f"🟢 **Sinyal KUAT BUY untuk {pair}**. Technical & sentimen selaras. Entry di pullback.")
        elif hybrid_score <= 35:
            st.error(f"🔴 **Sinyal KUAT SELL untuk {pair}**. Bearish pressure dominan. Fokus short setup.")
        elif 50 <= hybrid_score < 65:
            st.info(f"🟡 **Sinyal MODERATE BUY untuk {pair}**. Bias bullish tapi perlu konfirmasi.")
        else:
            st.warning(f"⚪ **NEUTRAL / WAIT untuk {pair}**. Market sideways/no clear edge.")
        
        st.info("💡 *Tips: Tambahkan GROQ_API_KEY di Streamlit Secrets untuk insight AI yang lebih mendalam.*")

if __name__ == "__main__":
    main()
