# db_setup.py
# Purpose: create SQLite DB and tables used by the app.
import sqlite3

DB = "investmatch.db"

def create_tables():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Stocks metadata
    c.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        symbol TEXT PRIMARY KEY,
        name TEXT,
        sector TEXT,
        market_cap REAL,
        pe_ratio REAL,
        beta REAL,
        last_update TEXT
    )
    """)

    # Stock price history
    c.execute("""
    CREATE TABLE IF NOT EXISTS stock_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        date TEXT,
        close REAL
    )
    """)

    # Mutual funds metadata
    c.execute("""
    CREATE TABLE IF NOT EXISTS mutual_funds (
        scheme_code TEXT PRIMARY KEY,
        name TEXT,
        category TEXT,
        risk_level TEXT,
        last_update TEXT
    )
    """)

    # Mutual fund NAV history
    c.execute("""
    CREATE TABLE IF NOT EXISTS mf_navs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scheme_code TEXT,
        date TEXT,
        nav REAL
    )
    """)

    # User portfolio holdings (PortfoliQ)
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        quantity REAL,
        buy_price REAL,
        buy_date TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Database and tables created:", DB)

if __name__ == "__main__":
    create_tables()
