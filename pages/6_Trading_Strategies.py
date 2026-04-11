import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="🚀 Trading Strategies", layout="wide")

def main():
    st.title("🚀 Trading Strategies 2026")
    
    strategies = [
        "🌊 Elliott Wave + ICT (Deep Dive)",
        "⚡ Scalping",
        "📅 Day Trading",
        "🔄 Swing Trading",
        "🐢 Position Trading",
        "📈 Trend Following",
        "💥 Breakout & Pullback",
        "🎯 Mean Reversion",
        "🔥 Momentum",
        "📰 News Trading",
        "💱 Carry Trade"
    ]
    
    tabs = st.tabs(strategies)
    
    # TAB 1: ELLIOTT WAVE + ICT
    with tabs[0]:
        st.header("🌊 Integrasi Elliott Wave dengan ICT (SMC)")
        
        st.markdown("""
        ### 📖 Konsep Dasar Hybrid Approach
        
        Menggabungkan **Elliott Wave** (Struktur Makro) dengan **ICT/SMC** (Eksekusi Mikro).
        
        | Elliott Wave (Macro) | ICT / Smart Money (Micro) |
        |-------------------|-------------------------|
        | Struktur 5-wave impulse + 3-wave corrective | Order Block (OB), Fair Value Gap (FVG) |
        | Fibonacci ratios untuk target | BOS/CHOCH, Liquidity Sweep |
        | Rule-based counting | Price action confirmation |
        | Big picture | Precision entry |
        
        ### 🔗 Cara Menggabungkan (Step-by-Step)
        
        1. **Identifikasi Wave Structure (H4/D1):**
           - Tentukan apakah harga sedang di **Wave 2** (koreksi setelah impuls naik) atau **Wave 4**
           - Pastikan 3 aturan Elliott Wave tidak dilanggar
        
        2. **Tunggu Retracement ke Zona Fibonacci:**
           - Wave 2: Tunggu pullback ke area **50-61.8% Fibonacci** dari Wave 1
           - Wave 4: Tunggu pullback ke area **23.6-38.2% Fibonacci** dari Wave 3
        
        3. **Cari Zona ICT di Lower Timeframe (M15/M5):**
           - Di area Fib tersebut, cari **Order Block (OB)** atau **Fair Value Gap (FVG)**
           - Order Block: Candle terakhir sebelum pergerakan impulsif
           - FVG: Gap 3-candle yang belum terisi
        
        4. **Entry Trigger:**
           - Entry hanya saat terjadi **BOS (Break of Structure)** di lower timeframe
           - Tunggu candle close di atas/below structure
        
        5. **Risk Management:**
           - **SL:** Di bawah Order Block atau Liquidity Pool terdekat
           - **TP:** Fibonacci Extension 1.272 atau 1.618 dari Wave awal
        
        ### ⚠️ 3 Aturan Wajib Elliott Wave (TIDAK BOLEH DILANGGAR)
        
        1. **Wave 2 tidak boleh turun lebih dari 100% Wave 1**
           - Jika break low Wave 1, hitungan batal
        
        2. **Wave 3 tidak boleh menjadi wave terpendek** di antara Wave 1, 3, dan 5
           - Biasanya Wave 3 adalah yang terpanjang dan terkuat
        
        3. **Wave 4 tidak boleh overlap dengan area harga Wave 1**
           - Kecuali dalam Diagonal Triangle pattern
        
        ### 📐 Panduan Fibonacci
        
        - **Wave 2**: 50-61.8% retracement Wave 1
        - **Wave 3**: 1.618x extension Wave 1 (biasanya yang terpanjang)
        - **Wave 4**: 23.6-38.2% retracement Wave 3
        - **Wave 5**: 0.618x length of Wave 1-3
        """)
        
        # Visual Simulation
        st.subheader("📊 Simulasi Visual: Entry Wave 3 dengan ICT")
        
        dates = pd.date_range('2024-01-01', periods=50)
        prices = [1.1000]
        
        for i in range(1, 50):
            move = np.random.normal(0, 0.002)
            if 10 < i < 20:
                prices.append(prices[-1] - 0.005 + move)  # Wave 2 pullback
            elif 20 <= i < 40:
                prices.append(prices[-1] + 0.008 + move)  # Wave 3 impulse
            else:
                prices.append(prices[-1] + move)
        
        df = pd.DataFrame({'Date': dates, 'Price': prices})
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Price'],
            mode='lines',
            name='Price',
            line=dict(color='white', width=2)
        ))
        
        # Markers
        fig.add_annotation(x=df['Date'][9], y=df['Price'][9], text="End Wave 1", arrowhead=1, ax=0, ay=-30)
        fig.add_annotation(x=df['Date'][19], y=df['Price'][19], text="End Wave 2 (Entry Zone)", arrowhead=1, ax=20, ay=-30)
        fig.add_annotation(x=df['Date'][35], y=df['Price'][35], text="Wave 3?", arrowhead=1, ax=0, ay=30)
        
        # Order Block zone
        fig.add_shape(
            type="rect",
            x0=df['Date'][18],
            x1=df['Date'][22],
            y0=df['Price'][20] - 0.005,
            y1=df['Price'][20] + 0.005,
            fillcolor="green",
            opacity=0.3,
            line=dict(width=0)
        )
        fig.add_annotation(x=df['Date'][20], y=df['Price'][20] + 0.006, text="🟢 Bullish OB", showarrow=False, font=dict(color="green"))
        
        fig.update_layout(
            title="Simulasi: Entry di Order Block Wave 2 untuk Wave 3",
            height=400,
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("""
        💡 **Kunci Sukses**:
        - Gunakan Higher Timeframe (H4/D1) untuk menghitung Wave
        - Entry di Lower Timeframe (M15/M5) saat harga retest OB + muncul BOS
        - SL di bawah Order Block
        - TP di Fib extension 1.272/1.618
        """)
        
        with st.expander("❌ Common Mistakes (Kesalahan Umum)"):
            st.markdown("""
            - **Overcounting**: Memaksa hitungan Wave agar sesuai keinginan
            - **Ignoring News**: Membuka posisi tepat saat rilis berita High Impact
            - **Subjective Counting**: Hitungan harus objektif berdasarkan 3 aturan utama
            - **Entry Tanpa Konfirmasi**: Jangan entry hanya karena harga di Fib level
            - **SL Terlalu Ketat**: SL harus di luar OB untuk menghindari liquidity sweep
            """)
    
    # TAB 2: SCALPING
    with tabs[1]:
        st.header("⚡ Scalping Strategy")
        st.markdown("""
        **Timeframe**: M1-M5
        
        **Pairs**: EUR/USD, GBP/USD (high liquidity, low spread)
        
        **Session**: London/New York overlap (08:00-12:00 EST)
        
        **Setup**:
        - Price action: Pin bar, engulfing di support/resistance
        - Indikator: EMA 9 + EMA 21 cross + RSI divergence
        - Konfirmasi: Volume spike + BOS
        
        **Risk Management**:
        - SL: 5-10 pips
        - TP: 10-20 pips
        - Max risk: 0.5% per trade
        - Max 3 trades/jam
        
        **Pro Tips**:
        - Trade hanya saat London/New York session overlap
        - Hindari news high-impact (NFP, CPI, Central Bank)
        - Gunakan limit order, hindari market order
        - Close semua posisi sebelum news penting
        """)
    
    # TAB 3: DAY TRADING
    with tabs[2]:
        st.header("📅 Day Trading Strategy")
        st.markdown("""
        **Timeframe**: M15-H1
        
        **Hold Time**: Intraday (close semua posisi sebelum EOD)
        
        **Core Approach**:
        - Trend following dengan EMA 50 sebagai dynamic S/R
        - Entry di pullback ke EMA + candlestick confirmation
        - Target: 30-80 pips per trade
        
        **Session Strategy**:
        - **Asian Session** (20:00-04:00 EST): Range trading, mean reversion
        - **London Session** (03:00-12:00 EST): Breakout, momentum
        - **New York Session** (08:00-17:00 EST): Trend continuation, news reaction
        
        **Tools**:
        - Pivot Points (daily)
        - VWAP (Volume Weighted Average Price)
        - Volume Profile
        
        **Risk Management**:
        - SL: 20-40 pips
        - TP: 40-80 pips
        - Max risk: 1% per trade
        """)
    
    # TAB 4: SWING TRADING
    with tabs[3]:
        st.header("🔄 Swing Trading Strategy")
        st.markdown("""
        **Timeframe**: H4-D1
        
        **Hold Time**: 2-7 days
        
        **Entry Framework**:
        1. Identifikasi trend dengan EMA 50/200 (Golden/Death Cross)
        2. Tunggu pullback ke key Fib level (38.2-61.8%)
        3. Konfirmasi dengan RSI divergence + pattern breakout
        
        **Position Management**:
        - SL: Beyond recent swing high/low atau ATR x 2
        - TP: Fib extension 1.272-1.618 atau prior structure
        - Trailing stop: Move to BE setelah 1R profit, trail dengan EMA
        
        **Best For**:
        - Trader part-time
        - Fundamental + technical confluence
        - Less screen time required
        
        **Risk Management**:
        - SL: 50-100 pips
        - TP: 100-200 pips
        - Max risk: 1-2% per trade
        """)
    
    # TAB 5: POSITION TRADING
    with tabs[4]:
        st.header("🐢 Position Trading")
        st.markdown("""
        **Timeframe**: D1-W1
        
        **Hold Time**: Weeks to months
        
        **Core Strategy**:
        - Fundamental analysis driven (interest rates, economic data)
        - Technical untuk timing entry (major S/R, trendlines)
        - Hold positions for weeks or months
        
        **Risk Management**:
        - SL: Wide (100-300 pips) berdasarkan major structure
        - TP: Major Fib extensions atau fundamental targets
        - Position size kecil (0.5-1% risk)
        
        **Best For**:
        - Investor-trader
        - Patient capital
        - Long-term fundamental view
        """)
    
    # TAB 6-10: Other Strategies
    with tabs[5]:
        st.markdown("### 📈 Trend Following")
        st.markdown("""
        **Philosophy**: "The trend is your friend"
        
        **Indicators**:
        - ADX > 25 (strong trend)
        - Price above EMA 50/200 (uptrend) atau below (downtrend)
        - Entry pada pullback ke EMA atau trendline
        
        **Exit**:
        - Trailing stop dengan ATR atau EMA
        - Exit saat ADX < 20 (trend weakening)
        
        **Best Pairs**: Trending pairs (GBP/JPY, EUR/JPY)
        """)
    
    with tabs[6]:
        st.markdown("### 💥 Breakout & Pullback")
        st.markdown("""
        **Setup**: Identify consolidation range (rectangle, triangle, flag)
        
        **Entry Methods**:
        1. **Aggressive**: Entry saat breakout dengan volume spike
        2. **Conservative**: Wait for pullback ke broken resistance
        
        **Confirmation**:
        - Volume increase pada breakout
        - Candle close di luar range
        - No immediate rejection
        
        **False Breakout Filter**:
        - Wait for retest dan hold
        - Minimum 2% break dari range
        """)
    
    with tabs[7]:
        st.markdown("### 🎯 Mean Reversion")
        st.markdown("""
        **Concept**: Price tends to return to mean/average
        
        **Entry Signals**:
        - RSI < 30 (oversold) atau > 70 (overbought)
        - Price di luar Bollinger Bands (2 SD)
        - Stochastic divergence
        
        **Best Conditions**:
        - Ranging market (ADX < 20)
        - Support/resistance confluence
        - No major news pending
        
        **Risk**: Trending market bisa menyebabkan large loss
        """)
    
    with tabs[8]:
        st.markdown("### 🔥 Momentum Trading")
        st.markdown("""
        **Philosophy**: Ride strong moves with high velocity
        
        **Indicators**:
        - MACD histogram increasing
        - RSI 50-70 (strong but not overbought)
        - Volume above average
        
        **Entry**:
        - Breakout dengan momentum confirmation
        - Pullback shallow (23.6-38.2% Fib)
        
        **Exit**:
        - Momentum divergence
        - Volume drying up
        - Target 1:2 or 1:3 R:R
        """)
    
    with tabs[9]:
        st.markdown("### 📰 News Trading")
        st.markdown("""
        **High-Impact Events**:
        - Non-Farm Payrolls (NFP)
        - Central Bank Rate Decisions
        - CPI/Inflation data
        - GDP releases
        
        **Strategies**:
        1. **Straddle**: Buy stop + sell stop sebelum news
        2. **Directional**: Trade berdasarkan actual vs forecast
        3. **Fade**: Counter-trade initial spike (risky!)
        
        **Risk Management**:
        - Wider SL (volatility spike)
        - Reduce position size (50% normal)
        - Beware slippage dan spread widening
        """)
    
    with tabs[10]:
        st.markdown("### 💱 Carry Trade")
        st.markdown("""
        **Concept**: Profit from interest rate differential
        
        **Setup**:
        - Buy high-yield currency (AUD, NZD)
        - Sell low-yield currency (JPY, CHF)
        - Example: Long AUD/JPY (positive swap)
        
        **Requirements**:
        - Stable/rising risk sentiment
        - No major reversal in rate policy
        - Long-term horizon (months)
        
        **Risk**:
        - Sudden risk-off event
        - Central bank policy change
        - Currency depreciation > swap income
        """)
    
    st.markdown("---")
    st.warning("""
    > ⚠️ **DISCLAIMER**: Semua strategi di atas untuk tujuan edukasi. 
    > Backtest dan demo trade sebelum menggunakan real money. 
    > Past performance tidak menjamin hasil masa depan.
    """)

if __name__ == "__main__":
    main()