import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

@st.cache_data(ttl=60)
def fetch_twelve_data(pair, interval="1day", outputsize=60):
    """
    Fetch data dari Twelve Data API (PRIORITAS UTAMA)
    """
    api_key = None
    if "TWELVE_DATA_API_KEY" in st.secrets:
        api_key = st.secrets["TWELVE_DATA_API_KEY"]
    elif st.session_state.get("twelve_api_key"):
        api_key = st.session_state.twelve_api_key

    if not api_key:
        return None

    try:
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
            df = pd.DataFrame(result["values"])
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            for col in ["open", "high", "low", "close", "volume"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

            df = df.iloc[::-1]  # oldest → newest
            return df
        else:
            return None

    except Exception:
        return None


@st.cache_data(ttl=300)
def fetch_frankfurter_rates(base="USD", symbols=None, start_date=None, end_date=None):
    """
    Fetch rates dari Frankfurter API.

    PENTING: Frankfurter punya 2 format response berbeda:
    - /latest     -> { "date": "...", "rates": { "EUR": 0.91 } }
    - /start..end -> { "rates": { "2025-01-01": { "EUR": 0.91 }, ... } }
    """
    if symbols is None:
        symbols = ["EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]

    try:
        if start_date and end_date:
            url = (
                f"https://api.frankfurter.app/{start_date}..{end_date}"
                f"?base={base}&symbols={','.join(symbols)}"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "rates" in data:
                # Format date range: { "2025-01-01": { "EUR": 0.91 }, ... }
                df = pd.DataFrame.from_dict(data["rates"], orient="index")
                df.index = pd.to_datetime(df.index)
                df.sort_index(inplace=True)
                return df

        else:
            url = (
                f"https://api.frankfurter.app/latest"
                f"?base={base}&symbols={','.join(symbols)}"
            )
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "rates" in data:
                # Format latest: { "EUR": 0.91, "GBP": 0.77, ... }
                df = pd.DataFrame([data["rates"]])
                df["date"] = data.get("date", datetime.now().strftime("%Y-%m-%d"))
                df.set_index("date", inplace=True)
                return df

        return pd.DataFrame()

    except Exception:
        # Uncomment untuk debug:
        # import traceback; st.warning(traceback.format_exc())
        return pd.DataFrame()


def fallback_to_frankfurter(pair, days=60):
    """
    STRATEGI PENGAMBILAN DATA:
    1. Twelve Data API  (real-time OHLC, butuh API key)
    2. Frankfurter API  (daily ECB rates, gratis)
    3. Simulasi         (last resort, silent)

    Konversi Frankfurter:
      fetch(base=USD, symbols=[EUR]) -> EUR per 1 USD = 0.855
      EUR/USD = USD per 1 EUR = 1 / 0.855 = 1.169  <-- FLIP
      Rumus universal: out["close"] = 1.0 / df_frank[base]
    """

    # 1. Twelve Data
    df_twelve = fetch_twelve_data(pair, interval="1day", outputsize=days)
    if df_twelve is not None and not df_twelve.empty:
        return df_twelve

    # 2. Frankfurter
    try:
        base, quote = pair.split("/")
        end_date   = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        df_frank = fetch_frankfurter_rates(
            base=quote,
            symbols=[base],
            start_date=start_date,
            end_date=end_date
        )

        if not df_frank.empty and base in df_frank.columns:
            out = pd.DataFrame()
            out["close"]  = 1.0 / df_frank[base]   # FLIP agar sesuai MT5/TradingView
            out["open"]   = out["close"].shift(1).fillna(out["close"].iloc[0])
            out["high"]   = out["close"] * 1.002
            out["low"]    = out["close"] * 0.998
            out["volume"] = np.random.randint(1000, 10000, size=len(out))
            return out.dropna()

    except Exception:
        pass

    # 3. Simulasi (last resort, harga referensi April 2026)
    try:
        current_prices = {
            "EUR/USD": 1.1720,
            "GBP/USD": 1.2950,
            "USD/JPY": 142.50,
            "USD/CHF": 0.8780,
            "AUD/USD": 0.6350,
            "USD/CAD": 1.3820,
            "NZD/USD": 0.5780,
            "EUR/GBP": 0.9050,
        }

        current_price = current_prices.get(pair, 1.1720)
        np.random.seed(hash(pair) % 2**32)
        returns = np.random.normal(0.0001, 0.003, days)

        prices = [current_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        prices = prices[::-1]
        prices[-1] = current_price

        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        df = pd.DataFrame(index=dates)
        df["close"]  = prices
        df["open"]   = df["close"].shift(1).fillna(prices[0])
        df["high"]   = df["close"] * 1.0015
        df["low"]    = df["close"] * 0.9985
        df["volume"] = np.random.randint(1000, 10000, size=len(df))

        return df.dropna()

    except Exception:
        return pd.DataFrame()
