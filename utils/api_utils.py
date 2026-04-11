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
            # ✅ Date range query
            url = f"https://api.frankfurter.app/{start_date}..{end_date}?base={base}&symbols={','.join(symbols)}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "rates" in data:
                # Format date range: { "rates": { "2025-01-01": { "EUR": 0.91 }, ... } }
                df = pd.DataFrame.from_dict(data["rates"], orient="index")
                df.index = pd.to_datetime(df.index)
                df.sort_index(inplace=True)
                return df
        else:
            # ✅ Latest query
            url = f"https://api.frankfurter.app/latest?base={base}&symbols={','.join(symbols)}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "rates" in data:
                # Format latest: { "date": "2025-04-11", "rates": { "EUR": 0.91 } }
                df = pd.DataFrame([data["rates"]])
                df["date"] = data.get("date", datetime.now().strftime("%Y-%m-%d"))
                df.set_index("date", inplace=True)
                return df

        return pd.DataFrame()

    except Exception as e:
        # Uncomment baris ini kalau mau debug:
        # st.warning(f"Frankfurter error: {e}")
        return pd.DataFrame()


def fallback_to_frankfurter(pair, days=60):
    """
    Mengambil data historis forex.
    Prioritas: Frankfurter API → Simulasi (silent fallback).
    """
    # 1. Coba ambil data asli dari Frankfurter
    try:
        base, quote = pair.split("/")
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Frankfurter: base=quote berarti kita cari 1 quote = ? base
        # Contoh EUR/USD → base=USD, symbols=[EUR] → hasilnya EUR per 1 USD
        # Tapi kita mau USD/EUR (harga EUR dalam USD), jadi perlu di-flip
        df_real = fetch_frankfurter_rates(
            base=quote,
            symbols=[base],
            start_date=start_date,
            end_date=end_date
        )

        if not df_real.empty and base in df_real.columns:
            out = pd.DataFrame()
            out["close"] = 1 / df_real[base]
            out["open"] = out["close"].shift(1).fillna(out["close"].iloc[0])
            out["high"] = out["close"] * 1.002
            out["low"] = out["close"] * 0.998
            out["volume"] = np.random.randint(1000, 10000, size=len(out))
            return out.dropna()

    except Exception:
        pass

    # 2. Fallback ke simulasi jika API gagal (silent)
    try:
        base_prices = {
            "EUR/USD": 1.1720,
            "GBP/USD": 1.2850,
            "USD/JPY": 148.50,
            "USD/CHF": 0.8920,
            "AUD/USD": 0.6720,
            "USD/CAD": 1.3480,
            "NZD/USD": 0.6280,
            "EUR/GBP": 0.8620
        }

        start_price = base_prices.get(pair, 1.1720)

        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        np.random.seed(hash(pair) % 2**32)
        returns = np.random.normal(0.0001, 0.005, days)
        prices = [start_price]

        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))

        prices = np.array(prices)
        df = pd.DataFrame(index=dates)
        df["close"] = prices
        df["open"] = df["close"].shift(1).fillna(start_price)
        df["high"] = df["close"] * 1.002
        df["low"] = df["close"] * 0.998
        df["volume"] = np.random.randint(1000, 10000, size=len(df))

        return df.dropna()

    except Exception:
        return pd.DataFrame()
