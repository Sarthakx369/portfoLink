# metrics.py
# Purpose: Fetch stock prices (live via yfinance) and compute metrics like CAGR, Sharpe ratio, volatility

import yfinance as yf
import numpy as np
import pandas as pd

# -------------------------
# Fetch latest stock price
# -------------------------
def latest_price(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
        else:
            return None
    except Exception as e:
        print(f"[ERROR] latest_price failed for {symbol}: {e}")
        return None

# -------------------------
# Load price series (for backtesting)
# -------------------------
def load_price_series(symbol: str, period="1y", interval="1d"):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        if not hist.empty:
            return hist["Close"]
        else:
            return pd.Series(dtype=float)
    except Exception as e:
        print(f"[ERROR] load_price_series failed for {symbol}: {e}")
        return pd.Series(dtype=float)

# -------------------------
# CAGR calculation
# -------------------------
def cagr_from_series(price_series: pd.Series):
    if price_series.empty:
        return None
    try:
        start_price = price_series.iloc[0]
        end_price = price_series.iloc[-1]
        num_years = (price_series.index[-1] - price_series.index[0]).days / 365.25
        if start_price <= 0 or num_years <= 0:
            return None
        return (end_price / start_price) ** (1 / num_years) - 1
    except Exception as e:
        print(f"[ERROR] cagr_from_series failed: {e}")
        return None

# -------------------------
# Sharpe ratio (approximate)
# -------------------------
def sharpe_ratio(price_series: pd.Series, risk_free_rate=0.05):
    if price_series.empty:
        return None
    try:
        returns = price_series.pct_change().dropna()
        excess_returns = returns - (risk_free_rate / 252)  # daily excess returns
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else None
    except Exception as e:
        print(f"[ERROR] sharpe_ratio failed: {e}")
        return None

# -------------------------
# Volatility (annualized stdev of daily returns)
# -------------------------
def volatility(price_series: pd.Series):
    if price_series.empty:
        return None
    try:
        daily_vol = price_series.pct_change().dropna().std()
        return daily_vol * np.sqrt(252)  # annualized
    except Exception as e:
        print(f"[ERROR] volatility failed: {e}")
        return None
