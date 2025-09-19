import sqlite3
import os

def init_db():
    if not os.path.exists("portfolio.db"):
        conn = sqlite3.connect("portfolio.db")
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE user_portfolio (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            stock_symbol TEXT,
                            quantity INTEGER,
                            buy_price REAL
                        )''')

        cursor.execute('''CREATE TABLE user_preferences (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sectors TEXT,
                            risk_level TEXT,
                            timeframe TEXT
                        )''')

        conn.commit()
        conn.close()
        print("Database created with initial schema.")
