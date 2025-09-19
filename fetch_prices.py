# fetch_prices.py
# Purpose: fetch price history for tickers and store in stock_prices table
import sqlite3
import yfinance as yf
from datetime import datetime

DB = "investmatch.db"

TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SUNPHARMA.NS",
    "HINDUNILVR.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "AXISBANK.NS"
]

def store_prices(symbol, period="5y"):
    hist = yf.Ticker(symbol).history(period=period)
    if hist.empty:
        print("No price data for", symbol)
        return

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # optional: remove existing price rows for symbol if you want a clean insert
    # c.execute("DELETE FROM stock_prices WHERE symbol=?", (symbol,))
    for date, row in hist.iterrows():
        date_str = date.strftime("%Y-%m-%d")
        close = float(row["Close"])
        c.execute("INSERT INTO stock_prices (symbol, date, close) VALUES (?, ?, ?)",
                  (symbol, date_str, close))
    conn.commit()
    conn.close()
    print(f"Stored prices for {symbol}, rows:", len(hist))

if __name__ == "__main__":
    for s in TICKERS:
        try:
            store_prices(s)
        except Exception as e:
            print("Error storing prices for", s, e)
