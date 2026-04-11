import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="💭 Sentiment Analysis", layout="wide")

# ============================================================================
# SIMULATED SENTIMENT DATA (Real apps bisa connect ke API Myfxbook, IG, dll)
# ============================================================================
@st.cache_data(ttl=3600)
def get_sentiment_data():
    """Return sentiment data untuk semua major pairs"""
    return {
        "EUR/USD": {
            "retail_long": 68,
            "retail_short": 32,
            "institutional_net": 60000,
            "institutional_bias": "Bullish",
            "fear_greed": 53,
            "social_sentiment": "Neutral"
        },
        "GBP/USD": {
            "retail_long": 45,
            "retail_short": 55,
            "institutional_net": 17000,
            "institutional_bias": "Neutral",
            "fear_greed": 48,
            "social_sentiment": "Bearish"
        },
        "USD/JPY": {
            "retail_long": 32,
            "retail_short": 68,
            "institutional_net": -53000,
            "institutional_bias": "Bearish",
            "fear_greed": 62,
            "social_sentiment": "Bullish"
        },
        "USD/CHF": {
            "retail_long": 52,
            "retail_short": 48,
            "institutional_net": -7000,
            "institutional_bias": "Bearish",
            "fear_greed": 45,
            "social_sentiment": "Neutral"
        },
        "AUD/USD": {
            "retail_long": 65,
            "retail_short": 35,
            "institutional_net": 7000,
            "institutional_bias": "Bullish",
            "fear_greed": 58,
            "social_sentiment": "Bullish"
        },
        "USD/CAD": {
            "retail_long": 48,
            "retail_short": 52,
            "institutional_net": -4000,
            "institutional_bias": "Neutral",
            "fear_greed": 50,
            "social_sentiment": "Neutral"
        },
        "NZD/USD": {
            "retail_long": 71,
            "retail_short": 29,
            "institutional_net": 3000,
            "institutional_bias": "Neutral",
            "fear_greed": 55,
            "social_sentiment": "Bullish"
        },
        "EUR/GBP": {
            "retail_long": 38,
            "retail_short": 62,
            "institutional_net": -12000,
            "institutional_bias": "Bearish",
            "fear_greed": 42,
            "social_sentiment": "Bearish"
        }
    }

def calculate_sentiment_impact(pair, sentiment_data):
    """Hitung sentiment impact dan rekomendasi action"""
    if pair not in sentiment_data:
        return {"signal": "NEUTRAL", "score": 50, "reason": "Data tidak tersedia"}
    
    data = sentiment_data[pair]
    retail_long = data["retail_long"]
    inst_bias = data["institutional_bias"]
    
    score = 50
    reasons = []
    
    # Contrarian logic: Retail ekstrem = sinyal berlawanan
    if retail_long > 65:
        score -= 20
        reasons.append(f"🔴 Retail {retail_long}% LONG (contrarian SELL)")
    elif retail_long < 35:
        score += 20
        reasons.append(f"🟢 Retail {retail_long}% LONG (contrarian BUY)")
    else:
        reasons.append(f"🟡 Retail netral ({retail_long}% LONG)")
    
    # Institutional alignment
    if inst_bias == "Bullish":
        score += 15
        reasons.append("✅ Institusi Bullish")
    elif inst_bias == "Bearish":
        score -= 15
        reasons.append("✅ Institusi Bearish")
    else:
        reasons.append("⚪ Institusi Netral")
    
    # Fear & Greed extreme = potential reversal
    fg = data["fear_greed"]
    if fg < 25 or fg > 75:
        score += 10
        reasons.append(f"⚡ Fear & Greed extreme ({fg}/100) → potensi reversal")
    
    # Normalize score
    score = max(0, min(100, score))
    
    # Determine signal
    if score >= 65:
        signal = "BUY"
    elif score <= 35:
        signal = "SELL"
    else:
        signal = "NEUTRAL"
    
    return {
        "signal": signal,
        "score": score,
        "reason": " | ".join(reasons),
        "retail_long": retail_long,
        "inst_bias": inst_bias,
        "fear_greed": fg
    }

def main():
    st.title("💭 Sentiment Analysis")
    
    # Get sentiment data
    sentiment_data = get_sentiment_data()
    
    # ========================================================================
    # SECTION 1: COT REPORT
    # ========================================================================
    st.header("📊 COT Report (Commitment of Traders)")
    
    cot_rows = []
    for pair, data in sentiment_data.items():
        cot_rows.append({
            "Pair": pair,
            "Inst. Net Position": f"{data['institutional_net']:+,}",
            "Inst. Bias": data["institutional_bias"],
            "Signal": "🟢 Bullish" if data["institutional_bias"] == "Bullish" else "🔴 Bearish" if data["institutional_bias"] == "Bearish" else "🟡 Neutral"
        })
    
    st.dataframe(pd.DataFrame(cot_rows), use_container_width=True, hide_index=True)
    st.info("💡 **Cara Baca**: Net Long Tinggi = Institusi akumulasi (bullish). Net Short Tinggi = Institusi distribusi (bearish).")
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 2: FEAR & GREED INDEX
    # ========================================================================
    st.header("😨😋 Fear & Greed Index")
    
    # Average fear_greed dari semua pairs
    avg_fg = sum(d["fear_greed"] for d in sentiment_data.values()) / len(sentiment_data)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Overall Market Sentiment", f"{avg_fg:.0f}/100")
        if avg_fg < 25:
            st.error("🔴 **Extreme Fear** - Potential buying opportunity")
        elif avg_fg < 45:
            st.warning("🟠 **Fear** - Market cautious")
        elif avg_fg <= 60:
            st.info("🔵 **Neutral** - Balanced sentiment")
        elif avg_fg < 75:
            st.success("🟢 **Greed** - Market optimistic")
        else:
            st.error("🔴 **Extreme Greed** - Potential correction")
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_fg,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Market Sentiment Gauge"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 25], 'color': '#c0392b'},
                    {'range': [25, 45], 'color': '#e74c3c'},
                    {'range': [45, 55], 'color': '#f39c12'},
                    {'range': [55, 75], 'color': '#27ae60'},
                    {'range': [75, 100], 'color': '#229954'}
                ],
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 3: RETAIL SENTIMENT (CONTRARIAN)
    # ========================================================================
    st.header("👥 Retail Sentiment (Contrarian Indicator)")
    
    retail_df = pd.DataFrame([
        {
            "Pair": pair,
            "% Long": data["retail_long"],
            "% Short": data["retail_short"],
            "Contrarian Signal": "🔴 SELL" if data["retail_long"] > 65 else "🟢 BUY" if data["retail_long"] < 35 else "⚪ NEUTRAL"
        }
        for pair, data in sentiment_data.items()
    ])
    
    st.dataframe(retail_df, use_container_width=True, hide_index=True)
    
    st.warning("""
    ⚠️ **Retail Sentiment adalah Contrarian Indicator**:
    
    - Retail traders sering salah di turning point market
    - Jika **>65% retail LONG** → Pertimbangkan posisi **SHORT**
    - Jika **>65% retail SHORT** → Pertimbangkan posisi **LONG**
    - Institusi sering mengambil liquidity dari retail sebelum reversal
    """)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 4: SENTIMENT IMPACT PER PAIR (NEW FEATURE!)
    # ========================================================================
    st.header("🎯 Sentiment Impact on Your Trades")
    
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    # Pair selector
    selected_pair = st.selectbox("Pilih Pair untuk Analisa Sentiment:", list(sentiment_data.keys()), 
                                index=list(sentiment_data.keys()).index(pair) if pair in sentiment_data else 0)
    
    impact = calculate_sentiment_impact(selected_pair, sentiment_data)
    
    # Display Impact Card
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Retail Long %", f"{impact['retail_long']}%", 
                 "High" if impact['retail_long'] > 65 else "Low" if impact['retail_long'] < 35 else "Normal")
    
    with col2:
        st.metric("Institutional Bias", impact['inst_bias'])
    
    with col3:
        st.metric("Fear & Greed", f"{impact['fear_greed']}/100")
    
    with col4:
        signal_icon = "🟢" if impact["signal"] == "BUY" else "🔴" if impact["signal"] == "SELL" else "🟡"
        st.metric("Sentiment Signal", f"{signal_icon} {impact['signal']}")
    
    st.markdown(f"### 📋 Analisa Detail: {selected_pair}")
    st.info(f"**Alasan**: {impact['reason']}")
    
    # Visual: Sentiment Balance Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Retail Long", "Retail Short"],
        y=[impact['retail_long'], 100 - impact['retail_long']],
        name="Retail Sentiment",
        marker_color=["red" if impact['retail_long'] > 50 else "green", "green" if impact['retail_long'] > 50 else "red"]
    ))
    fig.update_layout(
        title=f"Retail Sentiment Balance: {selected_pair}",
        height=300,
        template="plotly_dark",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Action Recommendation
    st.markdown("### 💡 Rekomendasi Trading Berdasarkan Sentiment")
    
    if impact["signal"] == "BUY":
        st.success(f"""
        ✅ **Sentiment mendukung BUY {selected_pair}**
        
        - Retail {impact['retail_long']}% LONG → {'Konfirmasi bullish' if impact['retail_long'] < 35 else 'Netral'}
        - Institusi {impact['inst_bias'].lower()} → {'Sejalan dengan BUY' if impact['inst_bias'] == 'Bullish' else 'Perlu konfirmasi teknikal'}
        - Fear & Greed {impact['fear_greed']}/100 → {'Potensi reversal dari extreme' if impact['fear_greed'] < 25 or impact['fear_greed'] > 75 else 'Netral'}
        
        **Action**: Pertimbangkan entry BUY dengan konfirmasi teknikal.
        """)
    elif impact["signal"] == "SELL":
        st.error(f"""
        ❌ **Sentiment mendukung SELL {selected_pair}**
        
        - Retail {impact['retail_long']}% LONG → {'Contrarian SELL signal' if impact['retail_long'] > 65 else 'Netral'}
        - Institusi {impact['inst_bias'].lower()} → {'Sejalan dengan SELL' if impact['inst_bias'] == 'Bearish' else 'Perlu konfirmasi teknikal'}
        - Fear & Greed {impact['fear_greed']}/100 → {'Potensi reversal dari extreme' if impact['fear_greed'] < 25 or impact['fear_greed'] > 75 else 'Netral'}
        
        **Action**: Pertimbangkan entry SELL dengan konfirmasi teknikal.
        """)
    else:
        st.warning(f"""
        ⚪ **Sentiment NEUTRAL untuk {selected_pair}**
        
        - Tidak ada edge jelas dari sentiment
        - Retail dan institusi tidak aligned
        - Fear & Greed di zona netral
        
        **Action**: Fokus pada analisa teknikal & fundamental. Sentiment tidak memberikan sinyal kuat.
        """)
    
    st.markdown("---")
    
    # ========================================================================
    # SECTION 5: HOW TO USE SENTIMENT IN TRADING
    # ========================================================================
    with st.expander("📚 Cara Menggunakan Sentiment dalam Trading"):
        st.markdown("""
        ### 🎯 Integrasi Sentiment dengan Strategi Trading
        
        **1. Sebagai Filter Konfirmasi**
        ```
        Technical: BUY signal
        Fundamental: BUY bias
        Sentiment: BUY signal
        → HIGH PROBABILITY SETUP ✅
        
        Technical: BUY signal
        Sentiment: SELL signal (contrarian)
        → WAIT atau entry dengan size lebih kecil ⚠️
        ```
        
        **2. Sebagai Early Warning Reversal**
        ```
        Price rally kuat + RSI overbought
        + Fear & Greed "Extreme Greed" (85+)
        + Retail 75% LONG
        → Potensi reversal bearish 🔄
        ```
        
        **3. Menghindari Crowded Trades**
        ```
        Jika semua orang sudah BUY:
        - Tidak ada buyer baru tersisa
        - Institusi mulai distribute
        - Market rentan drop tajam
        
        Sentiment analysis bantu hindari "buying the top"
        ```
        
        ### ⚠️ Limitasi Sentiment Analysis
        - Data retail sentiment bisa bias (hanya dari broker tertentu)
        - COT Report delay 3 hari
        - Sentiment ekstrem bisa bertahan lebih lama dari yang diperkirakan
        - Selalu konfirmasi dengan price action sebelum entry
        """)
    
    st.caption(f"🔄 Data sentiment updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
