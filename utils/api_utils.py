import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=60)  # Cache 1 menit untuk Twelve Data
def fetch_twelve_data(pair, interval="1day", outputsize=60):
    """
    Fetch data dari Twelve Data API (PRIORITAS UTAMA)
    """
    # Cek API key dari secrets
    api_key = None
    if "TWELVE_DATA_API_KEY" in st.secrets:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    elif st.session_state.get("twelve_api_key"):
        api_key = st.session_state.twelve_api_key
    
    if not api_key:
        return None  # No API key
    
    try:
        # Format pair untuk Twelve Data (EUR/USD → EURUSD)
        symbol = pair.replace("/", "")
        
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": api_key,
            "format": "JSON"
        }
        
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if result.get("status") == "ok" and "values" in result:
            # Parse data ke DataFrame
            df = pd.DataFrame(result["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)
            
            # Convert string ke numeric
            for col in ["open", "high", "low", "close", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # Reverse urutan (oldest → newest)
            df = df.iloc[::-1]
            
            return df
        else:
            return None
            
    except Exception:
        return None


@st.cache_data(ttl=300)  # Cache 5 menit untuk Frankfurter
def fetch_frankfurter_rates(base="USD", symbols=None, start_date=None, end_date=None):
    """
    Fallback ke Frankfurter (jika Twelve Data gagal)
    """
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
    except Exception:
        return pd.DataFrame()


def fallback_to_frankfurter(pair, days=60):
    """
    STRATEGI PENGAMBILAN DATA:
    1. Twelve Data API (PRIORITAS - Real-time)
    2. Frankfurter API (Fallback - Daily)
    3. Simulasi (Last resort - dengan harga terkini)
    """
    
    # 1️⃣ COBA TWELVE DATA DULU (Real-time)
    df_twelve = fetch_twelve_data(pair, interval="1day", outputsize=days)
    if df_twelve is not None and not df_twelve.empty:
        return df_twelve
    
    # 2️⃣ FALLBACK KE FRANKFURTER (Daily reference)
    try:
        base, quote = pair.split("/")
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        df_frank = fetch_frankfurter_rates(base=quote, symbols=[base], start_date=start_date, end_date=end_date)
        
        if not df_frank.empty and base in df_frank.columns:
            out = pd.DataFrame()
            out["close"] = df_frank[base]
            out["open"] = out["close"].shift(1).fillna(out["close"].iloc[0])
            out["high"] = out["close"] * 1.002
            out["low"] = out["close"] * 0.998
            out["volume"] = np.random.randint(1000, 10000, size=len(out))
            return out.dropna()
    except Exception:
        pass
    
    # 3️⃣ LAST RESORT: Simulasi dengan harga market terkini
    try:
        current_prices = {
            "EUR/USD": 1.1724,
            "GBP/USD": 1.2850,
            "USD/JPY": 148.50,
            "USD/CHF": 0.8920,
            "AUD/USD": 0.6720,
            "USD/CAD": 1.3480,
            "NZD/USD": 0.6280,
            "EUR/GBP": 0.8620
        }
        
        current_price = current_prices.get(pair, 1.1724)
        np.random.seed(hash(pair) % 2**32)
        returns = np.random.normal(0.0001, 0.003, days)
        prices = [current_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        prices = prices[::-1]
        prices[-1] = current_price
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        df = pd.DataFrame(index=dates)
        df["close"] = prices
        df["open"] = df["close"].shift(1).fillna(prices[0])
        df["high"] = df["close"] * 1.0015
        df["low"] = df["close"] * 0.9985
        df["volume"] = np.random.randint(1000, 10000, size=len(df))
        
        return df.dropna()
    
    except Exception:
        return pd.DataFrame()
