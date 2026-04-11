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

# ============================================================================
# SENTIMENT DATA (Same as Sentiment Analysis page)
# ============================================================================
@st.cache_data(ttl=3600)
def get_sentiment_data():
    return {
        "EUR/USD": {"retail_long": 68, "institutional_bias": "Bullish", "fear_greed": 53},
        "GBP/USD": {"retail_long": 45, "institutional_bias": "Neutral", "fear_greed": 48},
        "USD/JPY": {"retail_long": 32, "institutional_bias": "Bearish", "fear_greed": 62},
        "USD/CHF": {"retail_long": 52, "institutional_bias": "Bearish", "fear_greed": 45},
        "AUD/USD": {"retail_long": 65, "institutional_bias": "Bullish", "fear_greed": 58},
        "USD/CAD": {"retail_long": 48, "institutional_bias": "Neutral", "fear_greed": 50},
        "NZD/USD": {"retail_long": 71, "institutional_bias": "Neutral", "fear_greed": 55},
        "EUR/GBP": {"retail_long": 38, "institutional_bias": "Bearish", "fear_greed": 42}
    }

def calculate_sentiment_score(pair, sentiment_data):
    """Calculate sentiment score dengan contrarian logic"""
    if pair not in sentiment_data:
        return 50, "Data tidak tersedia"
    
    data = sentiment_data[pair]
    retail_long = data["retail_long"]
    inst_bias = data["institutional_bias"]
    fg = data["fear_greed"]
    
    score = 50
    reasons = []
    
    # Contrarian: Retail ekstrem = sinyal berlawanan
    if retail_long > 65:
        score -= 20
        reasons.append(f"Retail {retail_long}% LONG → contrarian bearish")
    elif retail_long < 35:
        score += 20
        reasons.append(f"Retail {retail_long}% LONG → contrarian bullish")
    
    # Institutional alignment
    if inst_bias == "Bullish":
        score += 15
        reasons.append("Institusi bullish")
    elif inst_bias == "Bearish":
        score -= 15
        reasons.append("Institusi bearish")
    
    # Fear & Greed extreme
    if fg < 25 or fg > 75:
        score += 10
        reasons.append(f"Fear & Greed extreme ({fg}) → potensi reversal")
    
    return max(0, min(100, score)), " | ".join(reasons) if reasons else "Netral"

def main():
    st.title("🤖 AI Analysis & Hybrid Scoring")
    
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    # Fetch technical data
    df = fallback_to_frankfurter(pair, days=60)
    
    # Calculate technical score
    tech_score = 50
    rsi = 50
    
    if not df.empty and "close" in df.columns:
        df = calculate_all_indicators(df)
        rsi = df.iloc[-1]["rsi_14"]
        price = df.iloc[-1]["close"]
        sma = df.iloc[-1]["sma_20"]
        
        if rsi < 30:
            tech_score = 80
        elif rsi > 70:
            tech_score = 20
        elif price > sma:
            tech_score = 60
        else:
            tech_score = 40
    
    # Calculate fundamental score (simulated)
    fund_score = 50
    
    # Calculate sentiment score (WITH DEEP INTEGRATION)
    sentiment_data = get_sentiment_data()
    sent_score, sent_reason = calculate_sentiment_score(pair, sentiment_data)
    
    # Hybrid score
    hybrid_score = round(tech_score * 0.5 + fund_score * 0.3 + sent_score * 0.2, 1)
    
    # ========================================================================
    # DISPLAY SCORES
    # ========================================================================
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Technical", f"{tech_score}/100")
    col2.metric("Fundamental", f"{fund_score}/100")
    col3.metric("Sentiment", f"{sent_score}/100")
    col4.metric("Hybrid", f"{hybrid_score}/100")
    
    st.markdown("### 📈 Score Breakdown")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.progress(tech_score / 100)
        st.caption("Technical (50%)")
    with c2:
        st.progress(fund_score / 100)
        st.caption("Fundamental (30%)")
    with c3:
        st.progress(sent_score / 100)
        st.caption("Sentiment (20%)")
    
    st.markdown("---")
    
    # ========================================================================
    # SENTIMENT DETAIL SECTION (NEW!)
    # ========================================================================
    st.subheader("💭 Sentiment Analysis Detail")
    
    if pair in sentiment_
        data = sentiment_data[pair]
        
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.metric("Retail Long %", f"{data['retail_long']}%")
        with col_s2:
            st.metric("Institutional Bias", data["institutional_bias"])
        with col_s3:
            st.metric("Fear & Greed", f"{data['fear_greed']}/100")
        
        st.caption(f"📊 Sentiment Impact: {sent_reason}")
    
    st.markdown("---")
    
    # ========================================================================
    # AI INSIGHT
    # ========================================================================
    st.subheader("💡 AI Insight (Bahasa Indonesia)")
    
    # Groq Integration (if available)
    if "GROQ_API_KEY" in st.secrets:
        try:
            from groq import Groq
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            context = f"""
            Pair: {pair}
            Technical Score: {tech_score}/100 (RSI: {rsi:.1f})
            Fundamental Score: {fund_score}/100
            Sentiment Score: {sent_score}/100 ({sent_reason})
            Hybrid Score: {hybrid_score}/100
            """
            
            with st.spinner("🤖 AI sedang menganalisa..."):
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are a professional forex trading assistant. Provide concise, actionable insights in Indonesian."},
                        {"role": "user", "content": f"Berdasarkan data berikut:\n{context}\nBerikan analisa singkat, sinyal utama, dan saran risk management."}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                st.markdown(completion.choices[0].message.content)
                st.success("✅ Analisis oleh Groq AI")
                
        except Exception as e:
            st.error(f"❌ Groq Error: {e}")
            # Fallback to rule-based insight
            generate_rule_based_insight(pair, hybrid_score, tech_score, sent_score, sent_reason)
    else:
        # Fallback to rule-based insight
        generate_rule_based_insight(pair, hybrid_score, tech_score, sent_score, sent_reason)
    
    st.info("""
    💡 **Metodologi Hybrid Score**:
    
    `Hybrid = Technical(50%) + Fundamental(30%) + Sentiment(20%)`
    
    - **70-100**: Strong signal → Entry dengan confidence tinggi
    - **55-69**: Moderate signal → Entry dengan size normal
    - **45-54**: Neutral → WAIT atau entry kecil
    - **30-44**: Weak opposite signal → Pertimbangkan arah berlawanan
    - **0-29**: Strong opposite signal → Entry opposite dengan confidence
    
    > ⚠️ Gunakan sebagai **filter probabilitas**, bukan sinyal entry otomatis.
    """)

def generate_rule_based_insight(pair, hybrid, tech, sent, sent_reason):
    """Fallback insight jika Groq tidak tersedia"""
    
    if hybrid >= 65:
        st.success(f"""
        🟢 **Sinyal KUAT BUY untuk {pair}**
        
        **Analisis**:
        - Technical score {tech}/100: {'Bullish momentum' if tech > 50 else 'Netral'}
        - Sentiment score {sent}/100: {sent_reason}
        - Konfluensi tinggi antara teknikal dan sentiment
        
        **Action**: 
        - Entry di pullback ke support
        - SL di bawah recent low
        - TP bertahap 1:2 R:R
        - Risk maksimal 1-2%
        """)
    elif hybrid <= 35:
        st.error(f"""
        🔴 **Sinyal KUAT SELL untuk {pair}**
        
        **Analisis**:
        - Technical score {tech}/100: {'Bearish pressure' if tech < 50 else 'Netral'}
        - Sentiment score {sent}/100: {sent_reason}
        - Konfluensi bearish dari multiple faktor
        
        **Action**:
        - Entry di rally ke resistance
        - SL di atas recent high
        - TP di Fib extension 1.272
        - Hindari counter-trend trades
        """)
    elif 50 <= hybrid < 65:
        st.info(f"""
        🟡 **Sinyal MODERATE BUY untuk {pair}**
        
        **Analisis**:
        - Bias bullish tapi perlu konfirmasi
        - Sentiment: {sent_reason}
        
        **Action**:
        - Entry dengan position size 0.5-1%
        - Tunggu konfirmasi candle close
        - Prioritaskan setup dengan confluence tinggi
        """)
    else:
        st.warning(f"""
        ⚪ **NEUTRAL / WAIT untuk {pair}**
        
        **Analisis**:
        - Market sideways / low confluence
        - Sentiment: {sent_reason}
        - Tidak ada edge jelas
        
        **Action**:
        - WAIT untuk setup lebih baik
        - Monitor economic calendar
        - Siapkan alert di key levels
        """)

if __name__ == "__main__":
    main()
