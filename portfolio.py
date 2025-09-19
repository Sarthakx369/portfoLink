# portfolio.py
# Purpose: Manage user portfolio & compute summary metrics

import sqlite3
import pandas as pd
from metrics import latest_price, load_price_series, cagr_from_series, sharpe_ratio, volatility

DB_PATH = "portfolio.db"

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
            continue  # Skip if no price found

        # Position values
        current_value = qty * price
        invested = qty * buy_price
        profit_loss = current_value - invested

        # Historical metrics
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
