import sqlite3
import os

def init_db():
    if not os.path.exists("portfolio.db"):
        conn = sqlite3.connect("portfolio.db")
        cursor = conn.cursor()

        # Create user portfolio table
        cursor.execute('''CREATE TABLE user_portfolio (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            stock_symbol TEXT,
                            quantity INTEGER,
                            buy_price REAL
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

# Run automatically when imported
init_db()
