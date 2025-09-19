# portfolio.py
# Purpose: user portfolio functions - add holding, view, compute performance,
# benchmark vs Nifty, and a simple simulator for investing in recommended picks.

import sqlite3
import pandas as pd
from metrics import latest_price, load_price_series, cagr_from_series
from datetime import datetime
import numpy as np
from math import sqrt

DB = "investmatch.db"

def add_holding(symbol, quantity, buy_price, buy_date=None):
    buy_date = buy_date or datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO user_portfolio (symbol, quantity, buy_price, buy_date) VALUES (?, ?, ?, ?)",
                 (symbol, float(quantity), float(buy_price), buy_date))
    conn.commit()
    conn.close()

def get_holdings_df():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM user_portfolio", conn)
    conn.close()
    return df

def calculate_portfolio():
    df = get_holdings_df()
    if df.empty:
        return None, None
    rows = []
    total_invested = 0.0
    total_current = 0.0
    for _, r in df.iterrows():
        sym = r['symbol']
        qty = r['quantity']
        buy_price = r['buy_price']
        invested = qty * buy_price
        price = latest_price(sym)
        if price is None:
            price = 0.0
        current_val = qty * price
        pl = current_val - invested
        pl_pct = (pl / invested) * 100 if invested else 0.0
        rows.append((sym, qty, buy_price, price, round(invested,2), round(current_val,2), round(pl,2), round(pl_pct,2)))
        total_invested += invested
        total_current += current_val
    df_out = pd.DataFrame(rows, columns=["Symbol", "Qty", "Buy Price", "Current Price", "Invested", "Current Value", "P&L", "P&L %"])
    # simple benchmark - Nifty 1y return using yfinance
    try:
        import yfinance as yf
        nifty = yf.Ticker("^NSEI")
        hist = nifty.history(period="1y")
        if not hist.empty:
            nifty_return = (hist['Close'].iloc[-1] / hist['Close'].iloc[0] - 1) * 100
        else:
            nifty_return = None
    except Exception:
        nifty_return = None

    portfolio_return_pct = ((total_current / total_invested) - 1) * 100 if total_invested > 0 else 0
    summary = {"Total Invested": round(total_invested,2), "Current Value": round(total_current,2),
               "Portfolio Return %": round(portfolio_return_pct,2), "Nifty 1y Return %": round(nifty_return,2) if nifty_return is not None else None}
    return df_out, summary

def simulate_investment(recs, total_amount):
    """
    recs: list of tuples from recommend_stocks, each tuple: (symbol,..., cagr, sharpe, vol) as defined earlier.
    This function divides total_amount equally across picks, computes expected portfolio CAGR as weighted avg of asset CAGRs,
    and approximates portfolio volatility assuming independence (variance weighted sum).
    Returns dict with expected CAGR, expected volatility, allocation breakdown.
    """
    if not recs:
        return None
    n = len(recs)
    allot = total_amount / n
    allocations = []
    cagr_list = []
    vol_list = []
    weights = []
    for item in recs:
        symbol = item[0]  # symbol
        # item format in recommender: (symbol, name, sector, score, cagr, sharpe, vol)
        cagr = item[4] if len(item) > 4 else None
        vol = item[6] if len(item) > 6 else None
        if cagr is None or vol is None:
            continue
        allocations.append((symbol, round(allot,2), round(cagr*100,2), round(vol*100,2)))
        cagr_list.append(cagr)
        vol_list.append(vol)
        weights.append(1.0/n)
    # expected CAGR weighted average
    expected_cagr = sum([w * cg for w, cg in zip(weights, cagr_list)])
    # approximate portfolio volatility assuming zero correlation
    expected_var = sum([ (w**2) * (v**2) for w, v in zip(weights, vol_list)])
    expected_vol = sqrt(expected_var)
    return {"expected_cagr_pct": round(expected_cagr*100,2), "expected_vol_pct": round(expected_vol*100,2), "allocations": allocations}
