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


def _get_twelve_data_key():
    """
    Helper aman untuk mengambil API Key.
    Prioritas: 1. Streamlit Secrets -> 2. Session State -> 3. None
    """
    # 1. Cek di Streamlit Secrets (Production / Cloud)
    if "TWELVE_DATA_API_KEY" in st.secrets:
        return st.secrets["TWELVE_DATA_API_KEY"]
    
    # 2. Fallback ke session state (Testing Lokal / Manual Input)
    if st.session_state.get("twelve_api_key"):
        return st.session_state.twelve_api_key
    
    return None


@st.cache_data(ttl=60)
def fetch_twelve_data(symbol, interval="1day", outputsize=100, indicators=None):
    """
    Fetch OHLC data dari Twelve Data API.
    API key otomatis diambil dari st.secrets atau session state.
    """
    api_key = _get_twelve_data_key()
    if not api_key:
        st.error("❌ Twelve Data API Key tidak ditemukan! Tambahkan di Streamlit Secrets.")
        return None

    try:
        symbol = symbol.replace("/", "")
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": api_key,
            "format": "JSON"
        }

        if indicators:
            for ind in indicators:
                if ind == "sma": params["with_sma"] = "20"
                elif ind == "ema": params["with_ema"] = "20"
                elif ind == "rsi": params["with_rsi"] = "time_period=14"
                elif ind == "macd": params["with_macd"] = "slow_period=26,fast_period=12,signal_period=9"
                elif ind == "bbands": params["with_bbands"] = "time_period=20,sd=2"
                elif ind == "atr": params["with_atr"] = "time_period=14"

        response = requests.get("https://api.twelvedata.com/time_series", params=params, timeout=15)

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "ok" and "values" in result:
                return result
            elif "message" in result:
                st.warning(f"⚠️ Twelve Data: {result['message']}")
        elif response.status_code == 401:
            st.error("❌ Twelve Data API Key Invalid! Cek ulang di Secrets.")
        elif response.status_code == 429:
            st.warning("⚠️ Twelve Data Rate Limit Exceeded (800 req/hari untuk free tier).")
        else:
            st.warning(f"⚠️ Twelve Data Error {response.status_code}")
        return None
    except Exception as e:
        st.warning(f"⚠️ Twelve Data Connection Error: {e}")
        return None


def parse_twelve_data_to_df(data):
    """Convert response Twelve Data ke DataFrame"""
    if not data or "values" not in data:
        return pd.DataFrame()
    try:
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df.set_index("datetime", inplace=True)
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df
    except Exception as e:
        st.error(f"❌ Error parsing Twelve Data: {e}")
        return pd.DataFrame()


def fallback_to_frankfurter(pair, days=60):
    """
    Generate OHLC mock data PURE (TIDAK tergantung API).
    Dijamin jalan 100% meskipun internet/API down.
    """
    try:
        base_prices = {
            "EUR/USD": 1.0850, "GBP/USD": 1.2650, "USD/JPY": 150.00,
            "USD/CHF": 0.8850, "AUD/USD": 0.6550, "USD/CAD": 1.3550,
            "NZD/USD": 0.6150, "EUR/GBP": 0.8580
        }
        start_price = base_prices.get(pair, 1.1000)
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        np.random.seed(hash(pair) % 2**32)  # Konsisten per pair
        
        returns = np.random.normal(0.0001, 0.005, days)
        prices = [start_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
            
        df = pd.DataFrame(index=dates)
        df["close"] = prices
        df["open"] = df["close"].shift(1).fillna(start_price)
        df["high"] = df["close"] * 1.002
        df["low"] = df["close"] * 0.998
        df["volume"] = np.random.randint(1000, 10000, size=len(df))
        
        return df.dropna()
    except Exception:
        return pd.DataFrame()
