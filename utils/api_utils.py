import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st


@st.cache_data(ttl=60)
def fetch_twelve_data(pair, interval="1day", outputsize=100):
    """
    Fetch OHLC dari Twelve Data API.
    Interval: 1min, 5min, 15min, 30min, 1h, 4h, 1day, 1week
    """
    api_key = None
    if hasattr(st, "secrets") and "TWELVE_DATA_API_KEY" in st.secrets:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    if not api_key:
        api_key = st.session_state.get("twelve_api_key")
    if not api_key:
        return None, "❌ API key Twelve Data belum diset. Masukkan di sidebar."

    try:
        symbol = pair.replace("/", "")
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol":     symbol,
            "interval":   interval,
            "outputsize": outputsize,
            "apikey":     api_key,
            "format":     "JSON",
        }

        response = requests.get(url, params=params, timeout=15)
        result   = response.json()

        if result.get("status") == "ok" and "values" in result:
            df = pd.DataFrame(result["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            for col in ["open", "high", "low", "close", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.iloc[::-1]   # oldest → newest
            return df, None

        # Tangkap error dari API (misal: rate limit, invalid symbol)
        err_msg = result.get("message", str(result))
        return None, f"❌ Twelve Data error: {err_msg}"

    except Exception as e:
        return None, f"❌ Koneksi gagal: {e}"


@st.cache_data(ttl=60)
def get_live_rate(pair):
    """
    Ambil harga live (bid/ask/close) untuk satu pair dari Twelve Data.
    Endpoint: /price (lebih ringan dari time_series)
    """
    api_key = None
    if hasattr(st, "secrets") and "TWELVE_DATA_API_KEY" in st.secrets:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    if not api_key:
        api_key = st.session_state.get("twelve_api_key")
    if not api_key:
        return None, "No API key"

    try:
        symbol = pair.replace("/", "")
        url    = "https://api.twelvedata.com/price"
        params = {"symbol": symbol, "apikey": api_key}

        r    = requests.get(url, params=params, timeout=10)
        data = r.json()

        if "price" in data:
            return float(data["price"]), None
        return None, data.get("message", "Unknown error")

    except Exception as e:
        return None, str(e)


def get_ohlc(pair, interval="1day", days=100):
    """
    Wrapper utama yang dipakai semua halaman.
    Mengembalikan (df, error_message).
    df = None jika gagal.
    """
    outputsize = days  # Twelve Data outputsize ≈ jumlah candle
    df, err = fetch_twelve_data(pair, interval=interval, outputsize=outputsize)
    return df, err


# Alias agar halaman lama yang masih import fallback_to_frankfurter tetap jalan
def fallback_to_frankfurter(pair, days=60):
    """
    DEPRECATED — dulu pakai Frankfurter sebagai fallback.
    Sekarang langsung ke Twelve Data. Kembalikan df atau DataFrame kosong.
    """
    df, err = get_ohlc(pair, interval="1day", days=days)
    if df is not None and not df.empty:
        return df
    # Tampilkan error jika ada
    if err:
        st.error(err)
    return pd.DataFrame()
