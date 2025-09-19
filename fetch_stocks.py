# fetch_stocks.py
# Purpose: fetch stock metadata (name, sector, market cap, PE, beta) for a small universe
# Edit the `TICKERS` list to include the Indian tickers you want to seed, for example from NSE.
import sqlite3
import yfinance as yf
from datetime import datetime

DB = "investmatch.db"

# Edit this list to include tickers you want to support
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

def store_metadata(symbol):
    t = yf.Ticker(symbol)
    info = t.info
    name = info.get("longName") or info.get("shortName") or symbol
    sector = info.get("sector") or "Unknown"
    market_cap = info.get("marketCap")
    pe = info.get("trailingPE")
    beta = info.get("beta")
    last_update = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO stocks (symbol, name, sector, market_cap, pe_ratio, beta, last_update)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (symbol, name, sector, market_cap, pe, beta, last_update))
    conn.commit()
    conn.close()
    print("Saved metadata for", symbol)

if __name__ == "__main__":
    for s in TICKERS:
        try:
            store_metadata(s)
        except Exception as e:
            print("Error", s, e)
