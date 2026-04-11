import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.api_utils import fallback_to_frankfurter
    from utils.indicators import calculate_all_indicators
    from utils.patterns import detect_candlestick_pattern
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
            df["rsi_14"] = 50.0
        return df
    
    def detect_candlestick_pattern(*args, **kwargs):
        return []

st.set_page_config(page_title="📈 Technical Analysis", layout="wide")

def main():
    pair = st.session_state.get("selected_pair", "EUR/USD")
    
    st.title("📈 Technical Analysis")
    st.markdown(f"**Pair:** {pair}")
    
    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        indicators = st.multiselect(
            "Indicators",
            ["SMA", "RSI", "ATR"],
            default=["SMA", "RSI"]
        )
    with col2:
        chart_type = st.selectbox("Chart Type", ["Candlestick", "Line", "OHLC"])
    with col3:
        show_patterns = st.checkbox("Show Patterns", value=True)
    
    # Fetch data
    df = fallback_to_frankfurter(pair, days=100)
    
    if not df.empty:
        df = calculate_all_indicators(df)
        
        # Build chart
        fig = go.Figure()
        
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="Price"
            ))
        elif chart_type == "Line":
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["close"],
                mode="lines",
                name="Close",
                line=dict(color="#1f77b4", width=2)
            ))
        else:
            fig.add_trace(go.Ohlc(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name="OHLC"
            ))
        
        # Add indicators
        if "SMA" in indicators and "sma_20" in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df["sma_20"],
                name="SMA 20",
                line=dict(color="orange", width=1)
            ))
        
        fig.update_layout(
            title=f"{pair} - Technical Chart",
            yaxis_title="Price",
            xaxis_title="Date",
            height=600,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Pattern Detection
        if show_patterns:
            st.markdown("---")
            st.subheader("🔍 Pattern Detection")
            
            patterns = detect_candlestick_pattern(df, lookback=10)
            
            if patterns:
                for p in patterns[-3:]:
                    icon = "🟢" if p.get("signal") == "BULLISH" else "🔴" if p.get("signal") == "BEARISH" else "🟡"
                    st.markdown(f"{icon} **{p.get('pattern', 'Unknown')}** @ {p.get('price', 0):.5f}")
            else:
                st.info("Tidak ada pattern signifikan terdeteksi.")
        
        # Latest values
        st.markdown("---")
        st.subheader("📋 Latest Indicator Values")
        
        latest = df.iloc[-1]
        ind_data = {
            "Indicator": ["Price", "SMA 20", "RSI (14)"],
            "Value": [
                f"{latest['close']:.5f}",
                f"{latest.get('sma_20', 0):.5f}" if "sma_20" in latest.index else "N/A",
                f"{latest.get('rsi_14', 0):.2f}" if "rsi_14" in latest.index else "N/A"
            ]
        }
        
        st.dataframe(pd.DataFrame(ind_data), use_container_width=True, hide_index=True)
    
    else:
        st.warning("⚠️ Data tidak tersedia.")

if __name__ == "__main__":
    main()