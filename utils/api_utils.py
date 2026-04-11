import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=300)
def fetch_frankfurter_rates(base="USD", symbols=None, start_date=None, end_date=None):
    """Fetch rates dari Frankfurter API (Gratis)"""
    if symbols is None:
        symbols = ["EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]
    try:
        if start_date and end_date:
            url = f"https://api.frankfurter.app/{start_date}..{end_date}?base={base}&symbols={','.join(symbols)}"
        else:
            url = f"https://api.frankfurter.app/latest?base={base}&symbols={','.join(symbols)}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "rates" in data:
            df = pd.DataFrame([data["rates"]])
            df["date"] = data.get("date", datetime.now().strftime("%Y-%m-%d"))
            df.set_index("date", inplace=True)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"⚠️ Frankfurter API Error: {e}")
        return pd.DataFrame()


def fallback_to_frankfurter(pair, days=60):
    """
    Generate OHLC mock data dengan base price UPDATED (Market 2026)
    + Warning banner kalau pakai data simulasi
    """
    # Tampilkan warning kalau pakai fallback
    st.info("⚠️ Menggunakan data simulasi (API tidak tersedia). Harga tidak real-time.")
    
    try:
        # BASE PRICE UPDATED - Market level terkini (Update sesuai market saat ini)
        base_prices = {
            "EUR/USD": 1.1720,  # ← UPDATE INI!
            "GBP/USD": 1.2850,
            "USD/JPY": 148.50,
            "USD/CHF": 0.8920,
            "AUD/USD": 0.6720,
            "USD/CAD": 1.3480,
            "NZD/USD": 0.6280,
            "EUR/GBP": 0.8620
        }
        
        start_price = base_prices.get(pair, 1.1720)
        
        # Generate dates
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        
        # Generate realistic price movement dengan random walk
        np.random.seed(hash(pair) % 2**32)  # Konsisten per pair
        returns = np.random.normal(0.0001, 0.005, days)
        prices = [start_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        prices = np.array(prices)
        
        # Create DataFrame
        df = pd.DataFrame(index=dates)
        df["close"] = prices
        df["open"] = df["close"].shift(1).fillna(start_price)
        df["high"] = df["close"] * 1.002
        df["low"] = df["close"] * 0.998
        df["volume"] = np.random.randint(1000, 10000, size=len(df))
        
        return df.dropna()
    
    except Exception as e:
        st.error(f"❌ Error generating mock data: {e}")
        return pd.DataFrame()
