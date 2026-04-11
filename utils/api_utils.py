import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st


def _get_api_key():
    """Ambil API key dari st.secrets (prioritas) atau session_state."""
    try:
        if "TWELVE_DATA_API_KEY" in st.secrets:
            return st.secrets["TWELVE_DATA_API_KEY"]
    except Exception:
        pass
    return st.session_state.get("twelve_api_key")


@st.cache_data(ttl=60)
def fetch_twelve_data(pair, interval="1day", outputsize=100):
    """Fetch OHLC dari Twelve Data API."""
    api_key = _get_api_key()
    if not api_key:
        st.error("❌ API key tidak ditemukan. Set TWELVE_DATA_API_KEY di Streamlit Secrets.")
        return None, "No API key"

    try:
        symbol = pair  # Twelve Data forex pakai format EUR/USD (dengan slash)
        url    = "https://api.twelvedata.com/time_series"
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
            df = df.iloc[::-1]  # oldest → newest
            return df, None

        err_msg = result.get("message", str(result))
        return None, f"❌ Twelve Data: {err_msg}"

    except Exception as e:
        return None, f"❌ Koneksi gagal: {e}"


@st.cache_data(ttl=30)
def get_live_rate(pair):
    """Ambil harga live dari Twelve Data endpoint /price."""
    api_key = _get_api_key()
    if not api_key:
        return None, "No API key"

    try:
        symbol = pair  # Twelve Data forex pakai format EUR/USD (dengan slash)
        r      = requests.get(
            "https://api.twelvedata.com/price",
            params={"symbol": symbol, "apikey": api_key},
            timeout=10
        )
        data = r.json()
        if "price" in data:
            return float(data["price"]), None
        return None, data.get("message", "Unknown error")

    except Exception as e:
        return None, str(e)


def get_ohlc(pair, interval="1day", days=100):
    """Wrapper utama — kembalikan (df, error_message)."""
    df, err = fetch_twelve_data(pair, interval=interval, outputsize=days)
    return df, err


def fallback_to_frankfurter(pair, days=60):
    """Alias lama → sekarang pakai Twelve Data."""
    df, err = get_ohlc(pair, interval="1day", days=days)
    if df is not None and not df.empty:
        return df
    if err:
        st.error(err)
    return pd.DataFrame()
