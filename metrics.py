# metrics.py
# Purpose: compute financial metrics used by recommender and simulator.
import sqlite3
import pandas as pd
import numpy as np
from math import sqrt

DB = "investmatch.db"

def load_price_series(symbol):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT date, close FROM stock_prices WHERE symbol=? ORDER BY date ASC", conn, params=(symbol,))
    conn.close()
    if df.empty:
        return None
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    return df['close']

def cagr_from_series(series):
    # series is pd.Series of closes indexed by date ascending
    if series is None or len(series) < 2:
        return None
    start = series.iloc[0]
    end = series.iloc[-1]
    days = (series.index[-1] - series.index[0]).days
    years = days / 365.25
    if years <= 0:
        return None
    cagr = (end / start) ** (1 / years) - 1
    return float(cagr)

def annual_volatility(series):
    if series is None or len(series) < 2:
        return None
    returns = series.pct_change().dropna()
    vol = returns.std(ddof=0) * sqrt(252)
    return float(vol)

def sharpe_ratio(series, risk_free_rate=0.04):
    # risk_free_rate in decimal yearly, e.g., 0.04 for 4%
    if series is None or len(series) < 2:
        return None
    returns = series.pct_change().dropna()
    ann_ret = returns.mean() * 252
    vol = returns.std(ddof=0) * sqrt(252)
    if vol == 0:
        return None
    sharpe = (ann_ret - risk_free_rate) / vol
    return float(sharpe)

# Small helper to get latest price for portfolio calc
def latest_price(symbol):
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT close FROM stock_prices WHERE symbol=? ORDER BY date DESC LIMIT 1", (symbol,)).fetchone()
    conn.close()
    if row:
        return float(row[0])
    return None
