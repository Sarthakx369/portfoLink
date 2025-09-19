# fetch_mfs.py
# Purpose: fetch AMFI NAVAll.txt contents and store scheme metadata and NAVs.
# This fetches a large CSV. It may be slow. For test you can restrict to a few scheme codes.
import sqlite3
import pandas as pd
from datetime import datetime

DB = "investmatch.db"
AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"  # AMFI text with separators

def fetch_and_store():
    df = pd.read_csv(AMFI_URL, sep=";")
    df = df.dropna(how='all')
    # The file contains columns: Scheme Code;ISIN Div Payout/ ISIN Growth;Scheme Name;Net Asset Value;Repurchase Price;Sale Price;Date
    # Column names may vary, inspect df.columns if error
    col_map = {col:col for col in df.columns}
    today = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    inserted = 0
    for _, row in df.iterrows():
        try:
            scheme_code = str(row['Scheme Code']).strip()
            name = str(row['Scheme Name']).strip()
            nav = float(row['Net Asset Value'])
            # category/risk not provided here, leave defaults
            c.execute("""
            INSERT OR REPLACE INTO mutual_funds (scheme_code, name, category, risk_level, last_update)
            VALUES (?, ?, ?, ?, ?)
            """, (scheme_code, name, None, "Medium", today))
            c.execute("INSERT INTO mf_navs (scheme_code, date, nav) VALUES (?, ?, ?)",
                      (scheme_code, row['Date'], nav))
            inserted += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    print("Stored mutual funds rows:", inserted)

if __name__ == "__main__":
    fetch_and_store()
