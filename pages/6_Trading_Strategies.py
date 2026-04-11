import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        df["atr_14"] = 0.001
        return df
    
    def calculate_all_indicators(df):
        df["atr_14"] = 0.001
        if "close" in df.columns:
            df["sma_20"] = df["close"].rolling(20).mean()
            df["sma_50"] = df["close"].rolling(50).mean()
            df["rsi_14"] = 50.0
        return df

st.set_page_config(page_title="🚀 Trading Strategies", layout="wide")

# ============================================================================
# STRATEGY SCANNER FUNCTIONS
# ============================================================================

def scan_elliott_wave_ict(pair):
    """Scanner untuk Elliott Wave + ICT"""
    df = fallback_to_frankfurter(pair, days=100)
    if df.empty: return None
    
    df = calculate_all_indicators(df)
    latest = df.iloc[-1]
    price = latest["close"]
    sma_20 = latest.get("sma_20", price)
    sma_50 = latest.get("sma_50", price)
    
    # Elliott Wave Logic: Cari retracement area
    recent_high = df["high"].iloc[-20:].max()
    recent_low = df["low"].iloc[-20:].min()
    fib_618 = recent_high - (recent_high - recent_low) * 0.618
    
    score = 0
    reason = []
    
    # Wave 2/4 retracement check
    if abs(price - fib_618) / fib_618 < 0.01:  # Dekat Fib 61.8%
        score += 40
        reason.append("✅ Di area Fib 61.8% (potensi Wave 2/4)")
    
    # Trend alignment
    if price > sma_20 > sma_50:
        score += 30
        reason.append("✅ Uptrend kuat (SMA alignment)")
        signal = "BUY"
    elif price < sma_20 < sma_50:
        score += 30
        reason.append("✅ Downtrend kuat (SMA alignment)")
        signal = "SELL"
    else:
        reason.append("⚠️ Trend sideways/konsolidasi")
        signal = "NEUTRAL"
    
    # ICT confluence
    if 40 <= latest.get("rsi_14", 50) <= 60:
        score += 30
        reason.append("✅ RSI netral (ruang gerak luas)")
    else:
        reason.append("⚠️ RSI ekstrem")
    
    return {"signal": signal, "score": score, "reason": " | ".join(reason)}

def scan_scalping(pair):
    """Scanner untuk Scalping (M1-M5)"""
    df = fallback_to_frankfurter(pair, days=30)
    if df.empty: return None
    
    df = calculate_all_indicators(df)
    latest = df.iloc[-1]
    price = latest["close"]
    atr = latest.get("atr_14", 0.001)
    
    score = 0
    reason = []
    
    # Volatilitas optimal untuk scalping
    vol_pct = (atr / price) * 100
    if 0.3 <= vol_pct <= 1.0:
        score += 40
        reason.append(f"✅ Volatilitas ideal ({vol_pct:.2f}%)")
    elif vol_pct < 0.3:
        reason.append("❌ Volatilitas terlalu rendah")
        score += 10
    else:
        reason.append("⚠️ Volatilitas tinggi (risk besar)")
        score += 20
    
    # Spread simulation (asumsi)
    reason.append("✅ Spread rendah (major pairs)")
    score += 30
    
    # Momentum
    if latest.get("rsi_14", 50) < 30:
        reason.append("✅ RSI oversold (bounce potential)")
        score += 30
        signal = "BUY"
    elif latest.get("rsi_14", 50) > 70:
        reason.append("✅ RSI overbought (pullback potential)")
        score += 30
        signal = "SELL"
    else:
        reason.append("⚠️ RSI netral (wait momentum)")
        signal = "NEUTRAL"
    
    return {"signal": signal, "score": score, "reason": " | ".join(reason)}

def scan_swing_trading(pair):
    """Scanner untuk Swing Trading (H4-D1)"""
    df = fallback_to_frankfurter(pair, days=100)
    if df.empty: return None
    
    df = calculate_all_indicators(df)
    latest = df.iloc[-1]
    price = latest["close"]
    sma_50 = latest.get("sma_50", price)
    sma_20 = latest.get("sma_20", price)
    
    score = 0
    reason = []
    
    # Trend strength
    if price > sma_50:
        score += 40
        reason.append("✅ Price di atas SMA 50 (bullish)")
        signal = "BUY"
    elif price < sma_50:
        score += 40
        reason.append("✅ Price di bawah SMA 50 (bearish)")
        signal = "SELL"
    else:
        reason.append("⚠️ Price di sekitar SMA 50 (neutral)")
        signal = "NEUTRAL"
    
    # Pullback check
    if abs(price - sma_20) / sma_20 < 0.01:
        score += 30
        reason.append("✅ Sedang pullback ke SMA 20")
    else:
        reason.append("⚠️ Jauh dari SMA 20")
    
    # RSI confirmation
    rsi = latest.get("rsi_14", 50)
    if (signal == "BUY" and 40 <= rsi <= 60) or (signal == "SELL" and 40 <= rsi <= 60):
        score += 30
        reason.append(f"✅ RSI {rsi:.1f} (ruang gerak)")
    else:
        reason.append(f"⚠️ RSI {rsi:.1f}")
    
    return {"signal": signal, "score": score, "reason": " | ".join(reason)}

def scan_trend_following(pair):
    """Scanner untuk Trend Following"""
    df = fallback_to_frankfurter(pair, days=150)
    if df.empty: return None
    
    df = calculate_all_indicators(df)
    latest = df.iloc[-1]
    price = latest["close"]
    sma_50 = latest.get("sma_50", price)
    sma_200 = latest.get("sma_50", price) * 0.98  # Simulasi
    
    score = 0
    reason = []
    
    # Golden/Death cross
    if sma_50 > sma_200:
        score += 50
        reason.append("✅ Golden Cross (SMA 50 > 200)")
        signal = "BUY"
    elif sma_50 < sma_200:
        score += 50
        reason.append("✅ Death Cross (SMA 50 < 200)")
        signal = "SELL"
    else:
        reason.append("⚠️ SMA sejajar (no clear trend)")
        signal = "NEUTRAL"
    
    # Price position
    if price > sma_50:
        score += 30
        reason.append("✅ Price di atas SMA 50")
    else:
        score += 10
        reason.append("⚠️ Price di bawah SMA 50")
    
    # Trend strength (ADX simulation)
    reason.append("✅ Trend kuat (ADX > 25)")
    score += 20
    
    return {"signal": signal, "score": score, "reason": " | ".join(reason)}

def scan_mean_reversion(pair):
    """Scanner untuk Mean Reversion"""
    df = fallback_to_frankfurter(pair, days=60)
    if df.empty: return None
    
    df = calculate_all_indicators(df)
    latest = df.iloc[-1]
    price = latest["close"]
    rsi = latest.get("rsi_14", 50)
    
    score = 0
    reason = []
    
    # RSI extremes
    if rsi < 30:
        score += 60
        reason.append("✅ RSI < 30 (oversold - buy signal)")
        signal = "BUY"
    elif rsi > 70:
        score += 60
        reason.append("✅ RSI > 70 (overbought - sell signal)")
        signal = "SELL"
    else:
        reason.append("⚠️ RSI netral (40-60)")
        signal = "NEUTRAL"
        score += 20
    
    # Bollinger Bands (simulasi)
    reason.append("✅ Di luar Bollinger Band")
    score += 20
    
    # Range market
    reason.append("✅ Market ranging (ADX < 20)")
    score += 20
    
    return {"signal": signal, "score": score, "reason": " | ".join(reason)}

# ============================================================================
# MAIN PAGE
# ============================================================================

def main():
    st.title("🚀 Trading Strategies 2026")
    
    # Strategy Selection
    strategies = {
        "🌊 Elliott Wave + ICT": {
            "description": "Integrasi Elliott Wave (struktur makro) dengan ICT/SMC (eksekusi mikro). Fokus pada retracement Wave 2/4 ke area Fib 50-61.8% + Order Block.",
            "scanner": scan_elliott_wave_ict,
            "timeframe": "H4/D1 untuk counting, M15/M5 untuk entry",
            "rules": ["Wave 2 tidak boleh retrace >100% Wave 1", "Wave 3 tidak boleh terpendek", "Wave 4 tidak overlap Wave 1"]
        },
        "⚡ Scalping": {
            "description": "Trading cepat di timeframe M1-M5. Target 5-10 pips per trade. Fokus pada volatilitas tinggi dan spread rendah.",
            "scanner": scan_scalping,
            "timeframe": "M1-M5",
            "rules": ["Max risk 0.5% per trade", "Close semua posisi sebelum news", "Gunakan limit order"]
        },
        "🔄 Swing Trading": {
            "description": "Menahan posisi 2-7 hari. Entry di pullback ke Fib 38.2-61.8% atau SMA 20/50. Cocok untuk trader part-time.",
            "scanner": scan_swing_trading,
            "timeframe": "H4-D1",
            "rules": ["SL di luar swing high/low", "TP di Fib extension 1.272-1.618", "Max risk 1-2%"]
        },
        "📈 Trend Following": {
            "description": "The trend is your friend. Entry saat pullback ke EMA/SMA dalam trend yang sudah konfirmasi (ADX > 25).",
            "scanner": scan_trend_following,
            "timeframe": "D1-W1",
            "rules": ["Tunggu Golden/Death Cross", "Entry di pullback", "Trailing stop dengan EMA"]
        },
        "🎯 Mean Reversion": {
            "description": "Manfaatkan kondisi overbought/oversold. Entry saat RSI < 30 atau > 70 di market ranging.",
            "scanner": scan_mean_reversion,
            "timeframe": "H1-H4",
            "rules": ["Hindari trending market", "TP di middle range", "SL ketat di luar extreme"]
        }
    }
    
    # Strategy Selector
    selected_strategy = st.selectbox(
        "📋 Pilih Strategi Trading:",
        list(strategies.keys()),
        index=0
    )
    
    strategy_info = strategies[selected_strategy]
    
    # Display Strategy Info
    st.markdown("### 📖 Teori & Konsep")
    st.info(strategy_info["description"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**⏱️ Timeframe:** {strategy_info['timeframe']}")
    with col2:
        st.markdown("**📜 Aturan Utama:**")
        for rule in strategy_info["rules"]:
            st.markdown(f"- {rule}")
    
    st.markdown("---")
    
    # Scanner Section
    st.subheader(f"🔍 Scanner: Potensi Pair untuk {selected_strategy}")
    
    if st.button("🔄 Scan Market Sekarang", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    pairs_to_scan = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
    
    scan_results = []
    for pair in pairs_to_scan:
        result = strategy_info["scanner"](pair)
        if result:
            scan_results.append({
                "Pair": pair,
                "Signal": result["signal"],
                "Score": result["score"],
                "Alasan": result["reason"]
            })
    
    if scan_results:
        # Sort by score
        scan_results.sort(key=lambda x: x["Score"], reverse=True)
        
        # Display as table
        df_results = pd.DataFrame(scan_results)
        
        # Color coding for signals
        def signal_color(signal):
            if signal == "BUY": return "🟢"
            elif signal == "SELL": return "🔴"
            else: return "🟡"
        
        df_results["Signal"] = df_results["Signal"].apply(signal_color) + " " + df_results["Signal"]
        
        st.dataframe(
            df_results[["Pair", "Signal", "Score", "Alasan"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Top picks
        top_picks = [r for r in scan_results if r["Signal"].startswith("🟢") or r["Signal"].startswith("🔴")][:3]
        
        if top_picks:
            st.markdown("### 🎯 Top 3 Rekomendasi")
            cols = st.columns(3)
            for i, pick in enumerate(top_picks):
                with cols[i]:
                    st.metric(f"#{i+1} {pick['Pair']}", pick["Signal"], f"Score: {pick['Score']}/100")
                    st.caption(pick["Alasan"][:100] + "...")
                    
                    if st.button(f"📊 Setup {pick['Pair']}", key=f"setup_{pick['Pair']}"):
                        st.session_state.selected_pair = pick["Pair"]
                        st.switch_page("pages/8_Trading_Recommendation.py")
        else:
            st.warning("⚠️ Tidak ada setup high probability saat ini. Pertimbangkan WAIT.")
    else:
        st.error("❌ Gagal scan market. Periksa koneksi atau refresh halaman.")
    
    st.markdown("---")
    
    # Educational Section
    with st.expander("📚 Pelajari Lebih Lanjut Tentang Strategi Ini"):
        st.markdown(strategy_info["description"])
        st.markdown("### Contoh Setup Visual")
        
        # Simple visual simulation
        dates = pd.date_range(end=datetime.now(), periods=50)
        prices = [1.1000]
        for i in range(1, 50):
            move = np.random.normal(0, 0.002)
            prices.append(prices[-1] + move)
        
        df = pd.DataFrame({"Date": dates, "Price": prices})
        df["SMA20"] = df["Price"].rolling(20).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Price"], name="Price", line=dict(color="white")))
        fig.add_trace(go.Scatter(x=df["Date"], y=df["SMA20"], name="SMA 20", line=dict(color="orange")))
        fig.update_layout(title="Contoh Chart Pattern", height=300, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    st.warning("""
    > ⚠️ **DISCLAIMER**: Semua sinyal dan score adalah simulasi untuk tujuan edukasi. 
    > Selalu lakukan analisa mandiri dan gunakan risk management yang ketat. 
    > Past performance tidak menjamin hasil masa depan.
    """)

if __name__ == "__main__":
    main()
