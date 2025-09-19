# portfolio.py

import sqlite3
import pandas as pd
from datetime import datetime
from math import sqrt
from metrics import latest_price, load_price_series, cagr_from_series, sharpe_ratio, volatility

DB_PATH = "portfolio.db"

# -------------------------
# Add a holding
# -------------------------
def add_holding(symbol, quantity, buy_price, buy_date=None):
    buy_date = buy_date or datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO user_portfolio (stock_symbol, quantity, buy_price) VALUES (?, ?, ?)",
        (symbol, float(quantity), float(buy_price))
    )
    conn.commit()
    conn.close()

# -------------------------
# Fetch portfolio from DB
# -------------------------
def fetch_portfolio():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM user_portfolio", conn)
    conn.close()
    return df

# -------------------------
# Demo fallback portfolio
# -------------------------
def demo_portfolio():
    return pd.DataFrame([
        {"stock_symbol": "AAPL", "quantity": 10, "buy_price": 150},
        {"stock_symbol": "MSFT", "quantity": 5, "buy_price": 280},
        {"stock_symbol": "GOOGL", "quantity": 3, "buy_price": 2500},
    ])

# -------------------------
# Calculate portfolio summary
# -------------------------
def calculate_portfolio():
    df = fetch_portfolio()

    # If DB is empty, load demo
    if df.empty:
        print("[INFO] Portfolio empty → using demo portfolio")
        df = demo_portfolio()

    results = []
    total_value = 0
    total_cost = 0

    for _, row in df.iterrows():
        sym = row["stock_symbol"]
        qty = row["quantity"]
        buy_price = row["buy_price"]

        # Get latest market price
        price = latest_price(sym)
        if price is None:
            print(f"[WARN] Could not fetch price for {sym}, skipping...")
            continue

        current_value = qty * price
        invested = qty * buy_price
        profit_loss = current_value - invested

        series = load_price_series(sym, period="1y")
        cagr = cagr_from_series(series)
        sharpe = sharpe_ratio(series)
        vol = volatility(series)

        results.append({
            "Symbol": sym,
            "Quantity": qty,
            "Buy Price": buy_price,
            "Latest Price": price,
            "Current Value": current_value,
            "Invested": invested,
            "Profit/Loss": profit_loss,
            "CAGR (1Y)": cagr,
            "Sharpe Ratio": sharpe,
            "Volatility": vol
        })

        total_value += current_value
        total_cost += invested

    df_results = pd.DataFrame(results)

    summary = {
        "Total Value": total_value,
        "Total Invested": total_cost,
        "Net P/L": total_value - total_cost,
        "Return %": ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
    }

    return df_results, summary

# -------------------------
# Simulate investments
# -------------------------
def simulate_investment(recs, total_amount):
    """
    recs: list of tuples like (symbol, name, sector, score, cagr, sharpe, vol)
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
        symbol = item[0]
        cagr = item[4] if len(item) > 4 else None
        vol = item[6] if len(item) > 6 else None
        if cagr is None or vol is None:
            continue
        allocations.append((symbol, round(allot, 2), round(cagr * 100, 2), round(vol * 100, 2)))
        cagr_list.append(cagr)
        vol_list.append(vol)
        weights.append(1.0 / n)
    expected_cagr = sum([w * cg for w, cg in zip(weights, cagr_list)])
    expected_var = sum([(w ** 2) * (v ** 2) for w, v in zip(weights, vol_list)])
    expected_vol = sqrt(expected_var)
    return {"expected_cagr_pct": round(expected_cagr * 100, 2),
            "expected_vol_pct": round(expected_vol * 100, 2),
            "allocations": allocations}
