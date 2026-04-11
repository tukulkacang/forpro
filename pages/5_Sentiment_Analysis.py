import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="💭 Sentiment Analysis", layout="wide")

def main():
    st.title("💭 Sentiment Analysis")
    
    # COT Report
    st.header("📊 COT Report (Commitment of Traders)")
    
    cot_df = pd.DataFrame({
        "Currency": ["EUR", "GBP", "JPY", "AUD", "CAD", "CHF"],
        "Non-Commercial Long": [185000, 95000, 45000, 72000, 88000, 28000],
        "Non-Commercial Short": [125000, 78000, 98000, 65000, 92000, 35000],
        "Net Position": [60000, 17000, -53000, 7000, -4000, -7000],
        "Signal": ["🟢 Bullish", "🟡 Neutral", "🔴 Bearish", "🟢 Bullish", "🔴 Bearish", "🔴 Bearish"]
    })
    
    st.dataframe(cot_df, use_container_width=True, hide_index=True)
    
    st.info("""
    💡 **Cara Membaca COT Report**:
    
    - **Non-Commercial Long**: Posisi long trader institusi besar (hedge funds)
    - **Non-Commercial Short**: Posisi short trader institusi besar
    - **Net Position**: Long - Short
    - **Net Long Tinggi** = Bias institusi BULLISH
    - **Net Short Tinggi** = Bias institusi BEARISH
    - COT Report dirilis setiap Jumat (data 3 hari sebelumnya)
    """)
    
    st.markdown("---")
    
    # Fear & Greed Index
    st.header("😨😋 Fear & Greed Index")
    
    # Simulated score
    fear_greed_score = 53
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Overall Market Sentiment", f"{fear_greed_score}/100")
        
        if fear_greed_score < 25:
            st.error("🔴 **Extreme Fear** - Potential buying opportunity")
        elif fear_greed_score < 45:
            st.warning("🟠 **Fear** - Market cautious")
        elif fear_greed_score <= 60:
            st.info("🔵 **Neutral** - Balanced sentiment")
        elif fear_greed_score < 75:
            st.success("🟢 **Greed** - Market optimistic")
        else:
            st.error("🔴 **Extreme Greed** - Potential correction")
    
    with col2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=fear_greed_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Market Sentiment Gauge"},
            delta={'reference': 50, 'increasing': {'color': "#27ae60"}, 'decreasing': {'color': "#e74c3c"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#1f77b4"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
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
    
    # Retail Sentiment
    st.header("👥 Retail Trader Sentiment (Contrarian Indicator)")
    
    retail_df = pd.DataFrame({
        "Pair": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"],
        "% Long": [68, 72, 35, 45, 65, 52],
        "% Short": [32, 28, 65, 55, 35, 48],
        "Contrarian Signal": ["🔴 SELL", "🔴 SELL", "🟢 BUY", "⚪ NEUTRAL", "🔴 SELL", "⚪ NEUTRAL"]
    })
    
    st.dataframe(retail_df, use_container_width=True, hide_index=True)
    
    st.warning("""
    ⚠️ **Retail Sentiment adalah Contrarian Indicator**:
    
    - Retail traders sering salah di turning point market
    - Jika **>65% retail LONG** → Pertimbangkan posisi **SHORT**
    - Jika **>65% retail SHORT** → Pertimbangkan posisi **LONG**
    - Institusi sering mengambil liquidity dari retail sebelum reversal
    """)
    
    st.markdown("---")
    
    # Social Media Sentiment
    st.header("💬 Social Media Sentiment (Simulated)")
    
    social_df = pd.DataFrame({
        "Pair": ["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USD"],
        "Mentions (24h)": [1250, 890, 654, 3420],
        "Positive %": [45, 38, 52, 68],
        "Neutral %": [35, 42, 30, 22],
        "Negative %": [20, 20, 18, 10],
        "Trend": ["📉 Bearish", "📉 Bearish", "📈 Bullish", "🤑 Very Bullish"]
    })
    
    st.dataframe(social_df, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()