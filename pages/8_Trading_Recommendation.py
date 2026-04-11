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
    from utils.calculations import calculate_position_size
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
        df["atr_14"] = 0.001
        return df
    
    def calculate_all_indicators(df):
        df["atr_14"] = 0.001
        if "close" in df.columns:
            df["sma_20"] = df["close"].rolling(20).mean()
            df["rsi_14"] = 50.0
        return df
    
    def calculate_position_size(balance, risk_pct, sl_pips, pip_val=10):
        return round((balance * (risk_pct/100)) / (sl_pips * pip_val), 2)

st.set_page_config(page_title="🎯 Trading Recommendation", layout="wide")

def scan_market_pairs():
    pairs_to_scan = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD", "EUR/GBP"]
    results = []
    
    for pair in pairs_to_scan:
        try:
            df = fallback_to_frankfurter(pair, days=50)
            if df.empty or "close" not in df.columns:
                continue
                
            df = calculate_all_indicators(df)
            latest = df.iloc[-1]
            
            price = latest["close"]
            sma = latest.get("sma_20", price)
            rsi = latest.get("rsi_14", 50)
            atr = latest.get("atr_14", 0.001)
            
            trend_score = 80 if price > sma else 20
            
            if 40 <= rsi <= 60:
                rsi_score = 75
            elif (30 <= rsi < 40) or (60 < rsi <= 70):
                rsi_score = 50
            else:
                rsi_score = 20
                
            vol_score = min(100, (atr / price) * 100000)
            total_score = (trend_score * 0.4) + (rsi_score * 0.3) + (vol_score * 0.3)
            
            results.append({
                "Pair": pair,
                "Setup Score": round(total_score, 1),
                "Trend": "🟢 Bullish" if price > sma else "🔴 Bearish",
                "RSI": f"{rsi:.1f}",
                "ATR": f"{atr:.5f}",
                "Signal": "BUY" if price > sma else "SELL"
            })
        except Exception:
            continue
            
    results.sort(key=lambda x: x["Setup Score"], reverse=True)
    return results

def main():
    st.title("🎯 Trading Recommendation")
    
    st.subheader("🔍 Market Scanner: Top Potential Pairs")
    st.caption("Sistem ranking berdasarkan Trend Alignment + RSI Momentum + Volatilitas Optimal")
    
    if st.button("🔄 Scan Market Sekarang", type="primary"):
        st.rerun()
        
    scan_results = scan_market_pairs()
    
    if scan_results:
        top_3 = scan_results[:3]
        cols = st.columns(3)
        for i, pick in enumerate(top_3):
            with cols[i]:
                st.metric(f"#{i+1} {pick['Pair']}", f"{pick['Setup Score']}/100", pick["Trend"])
                st.caption(f"RSI: {pick['RSI']} | ATR: {pick['ATR']}")
                
                if st.button(f"📊 Lihat Setup {pick['Pair']}", key=f"btn_{pick['Pair']}"):
                    st.session_state.selected_pair = pick["Pair"]
                    st.rerun()
    else:
        st.warning("⚠️ Scanner gagal memuat data.")

    st.markdown("---")
    
    pair = st.session_state.get("selected_pair", "EUR/USD")
    st.subheader(f"📈 Detailed Setup: {pair}")
    
    scenario = st.radio("Risk Profile", ["Conservative", "Moderate", "Aggressive"], horizontal=True)
    mult = {"Conservative": 2.5, "Moderate": 1.5, "Aggressive": 1.0}[scenario]
    
    df = fallback_to_frankfurter(pair, days=50)
    
    if not df.empty and "close" in df.columns:
        df = calculate_all_indicators(df)
        latest = df.iloc[-1]
        price = latest["close"]
        atr = latest.get("atr_14", 0.001)
        sma = latest.get("sma_20", price)
        
        direction = "BUY" if price > sma else "SELL"
        
        sl_dist = atr * mult
        
        if direction == "BUY":
            sl = price - sl_dist
            tp1 = price + (sl_dist * 2)
            tp2 = price + (sl_dist * 3)
        else:
            sl = price + sl_dist
            tp1 = price - (sl_dist * 2)
            tp2 = price - (sl_dist * 3)
        
        trend_icon = "🟢" if direction == "BUY" else "🔴"
        st.markdown(f"### {trend_icon} Signal: **{direction} {pair}**")
        st.caption(f"Berdasarkan: Harga {'di atas' if direction == 'BUY' else 'di bawah'} SMA 20")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Entry", f"{price:.5f}")
        c2.metric("Stop Loss", f"{sl:.5f}")
        c3.metric("TP 1", f"{tp1:.5f}")
        c4.metric("TP 2", f"{tp2:.5f}")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["close"], name="Price", line=dict(color="white")))
        
        line_color = "green" if direction == "BUY" else "red"
        fig.add_hline(y=price, line_dash="dash", line_color="gold", annotation_text="Entry")
        fig.add_hline(y=sl, line_dash="dot", line_color=line_color, annotation_text=f"SL ({direction})")
        fig.add_hline(y=tp1, line_dash="dot", line_color="lime" if direction == "BUY" else "orange", annotation_text="TP1")
        fig.add_hline(y=tp2, line_dash="dot", line_color="lime" if direction == "BUY" else "orange", annotation_text="TP2")
        
        fig.update_layout(title=f"{pair} - {direction} Setup", height=350, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 💰 Risk Calculator")
        bal = st.session_state.get("account_balance", 10000)
        risk = st.session_state.get("risk_per_trade", 1.0)
        pips = abs(price - sl) / 0.0001
        lots = calculate_position_size(bal, risk, pips, 10)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Position Size", f"{lots:.2f} lots")
        c2.metric("Risk Amount", f"${bal * (risk / 100):,.2f}")
        c3.metric("Risk:Reward", f"1:2.0 (TP1) | 1:3.0 (TP2)")
        
        st.markdown("### 📋 Trade Plan")
        rr_ratio = 2.0
        
        plan_df = pd.DataFrame({
            "Parameter": ["Pair", "Direction", "Entry Price", "Stop Loss", "Take Profit 1", "Take Profit 2", "Risk:Reward"],
            "Value": [pair, direction, f"{price:.5f}", f"{sl:.5f}", f"{tp1:.5f}", f"{tp2:.5f}", f"1:{rr_ratio:.1f}"]
        })
        st.dataframe(plan_df, use_container_width=True, hide_index=True)
        
        if direction == "BUY":
            st.success(f"✅ **Setup BUY {pair}** - Entry di {price:.5f}, SL di {sl:.5f}, TP1 di {tp1:.5f}")
        else:
            st.error(f"❌ **Setup SELL {pair}** - Entry di {price:.5f}, SL di {sl:.5f}, TP1 di {tp1:.5f}")
            
        st.warning("⚠️ **Disclaimer**: Simulasi edukatif. Gunakan risk management ketat. Trading forex berisiko tinggi.")
    else:
        st.error("❌ Data tidak tersedia. Cek koneksi atau refresh halaman.")

if __name__ == "__main__":
    main()
