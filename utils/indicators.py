import pandas as pd
import numpy as np


def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI)
    """
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calculate_all_indicators(df):
    """
    Calculate semua indikator teknikal
    """
    if df.empty or "close" not in df.columns:
        return df
    
    try:
        res = df.copy()
        
        # Moving Averages
        res["sma_20"] = res["close"].rolling(window=20).mean()
        res["sma_50"] = res["close"].rolling(window=50).mean()
        res["ema_12"] = res["close"].ewm(span=12, adjust=False).mean()
        res["ema_26"] = res["close"].ewm(span=26, adjust=False).mean()
        
        # RSI
        res["rsi_14"] = calculate_rsi(res["close"], period=14)
        
        # MACD
        res["macd"] = res["ema_12"] - res["ema_26"]
        res["macd_signal"] = res["macd"].ewm(span=9, adjust=False).mean()
        res["macd_hist"] = res["macd"] - res["macd_signal"]
        
        # Bollinger Bands
        res["bb_middle"] = res["close"].rolling(window=20).mean()
        bb_std = res["close"].rolling(window=20).std()
        res["bb_upper"] = res["bb_middle"] + (bb_std * 2)
        res["bb_lower"] = res["bb_middle"] - (bb_std * 2)
        
        # ATR
        if "high" in res.columns and "low" in res.columns:
            tr1 = res["high"] - res["low"]
            tr2 = abs(res["high"] - res["close"].shift())
            tr3 = abs(res["low"] - res["close"].shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            res["atr_14"] = tr.rolling(window=14).mean()
        else:
            res["atr_14"] = res["close"] * 0.001
        
        # Fill NaN values
        res = res.ffill().bfill()
        
        return res
    
    except Exception as e:
        st.error(f"❌ Error calculating indicators: {e}")
        return df