import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st


def fallback_to_frankfurter(pair, days=60):
    """
    LANGSUNG PAKAI DATA SIMULASI dengan harga market terkini.
    TANPA coba API dulu (biar cepat & harga update).
    """
    try:
        # HARGA MARKET TERKINI (Update sesuai kondisi market sekarang)
        base_prices = {
            "EUR/USD": 1.1720,  # <-- Harga MT5 saat ini!
            "GBP/USD": 1.2850,
            "USD/JPY": 148.50,
            "USD/CHF": 0.8920,
            "AUD/USD": 0.6720,
            "USD/CAD": 1.3480,
            "NZD/USD": 0.6280,
            "EUR/GBP": 0.8620
        }
        
        start_price = base_prices.get(pair, 1.1720)
        
        # Generate realistic price movement
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        np.random.seed(hash(pair) % 2**32)  # Konsisten per pair
        returns = np.random.normal(0.0001, 0.005, days)
        prices = [start_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        prices = np.array(prices)
        
        # Create OHLC DataFrame
        df = pd.DataFrame(index=dates)
        df["close"] = prices
        df["open"] = df["close"].shift(1).fillna(start_price)
        df["high"] = df["close"] * 1.002
        df["low"] = df["close"] * 0.998
        df["volume"] = np.random.randint(1000, 10000, size=len(df))
        
        return df.dropna()
    
    except Exception as e:
        return pd.DataFrame()
