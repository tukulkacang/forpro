import streamlit as st
import pandas as pd
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="🔄 Hybrid Approach", layout="wide")

def main():
    st.title("🔄 Hybrid Approach - Multi-Method Analysis")
    
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    st.markdown("### 🎯 Confluence Checklist")
    st.markdown("Centang metode yang memberikan sinyal searah untuk konfirmasi tinggi:")
    
    c1 = st.checkbox("✅ Elliott Wave Structure Valid")
    c2 = st.checkbox("✅ ICT Order Block / FVG Present")
    c3 = st.checkbox("✅ Fundamental Bias Aligned")
    c4 = st.checkbox("✅ Sentiment Confirmed (Contrarian)")
    
    score = sum([c1, c2, c3, c4]) * 25
    
    st.metric("Confluence Score", f"{score}/100")
    
    if score >= 75:
        st.success("""
        🟢 **HIGH PROBABILITY SETUP**
        
        - Minimal 3 metode aligned
        - Entry dengan confidence tinggi
        - Gunakan position size normal (1-2%)
        - SL ketat, TP bertahap
        """)
    elif score >= 50:
        st.warning("""
        🟡 **MODERATE SETUP**
        
        - 2 metode aligned
        - Tunggu konfirmasi tambahan
        - Gunakan position size lebih kecil (0.5-1%)
        - Prioritaskan setup dengan confluence tinggi
        """)
    else:
        st.error("""
        🔴 **LOW EDGE / WAIT**
        
        - <2 metode aligned
        - Market choppy / sideways
        - Hindari trading atau gunakan size sangat kecil
        - Tunggu setup lebih jelas
        """)
    
    st.info("""
    💡 **Hybrid Approach Philosophy**:
    
    Jangan bergantung pada satu metode saja!
    
    - ✅ **Technical Analysis**: Memberikan timing entry
    - ✅ **Elliott Wave**: Memberikan context struktur pasar
    - ✅ **ICT/SMC**: Memberikan precision entry
    - ✅ **Fundamental**: Memberikan directional bias
    - ✅ **Sentiment**: Memberikan contrarian signal
    
    **High Probability Setup** = Ketika SEMUA metode aligned!
    
    > ⚠️ **Disclaimer**: Hybrid score adalah tool untuk filter probabilitas, bukan jaminan profit. 
    > Selalu gunakan risk management dan trading plan yang disiplin.
    """)

if __name__ == "__main__":
    main()