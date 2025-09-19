import sqlite3
import os

DB = "investmatch.db"

def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        # Create user portfolio table (matches portfolio.py)
        cursor.execute('''CREATE TABLE user_portfolio (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            symbol TEXT,
                            quantity REAL,
                            buy_price REAL,
                            buy_date TEXT
                        )''')

        # Create user preferences table
        cursor.execute('''CREATE TABLE user_preferences (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sectors TEXT,
                            risk_level TEXT,
                            timeframe TEXT
                        )''')

        conn.commit()
        conn.close()
        print("Database created with initial schema.")
    else:
        print("Database already exists.")

# Run automatically
init_db()
