# recommender.py
# Purpose: recommend top stocks and mutual funds given user preferences.
import sqlite3
from metrics import load_price_series, cagr_from_series, annual_volatility, sharpe_ratio

DB = "investmatch.db"

def recommend_stocks(user_profile, top_n=5, years=3):
    """
    user_profile: dict with keys 'horizon','risk','sectors' (list)
    returns: list of tuples (symbol, name, sector, score, cagr, sharpe, vol)
    """
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT symbol, name, sector FROM stocks").fetchall()
    conn.close()

    candidates = []
    for symbol, name, sector in rows:
        # sector filter
        if user_profile.get("sectors"):
            if sector not in user_profile["sectors"]:
                continue

        series = load_price_series(symbol)
        cagr = cagr_from_series(series)
        vol = annual_volatility(series)
        sharpe = sharpe_ratio(series)

        if None in (cagr, vol, sharpe):
            continue

        # Basic risk filter: disallow high volatility for low risk users
        if user_profile.get("risk") == "low" and vol > 0.30:
            continue
        if user_profile.get("risk") == "medium" and vol > 0.50:
            # allow more volatile for medium
            pass

        # Simple score combining Sharpe and CAGR normalized
        # Note: cagr is decimal, sharpe is unitless, vol is decimal
        score = 0.6 * sharpe + 0.4 * (cagr * 100) / 10  # scale cagr to similar magnitude
        candidates.append((symbol, name, sector, score, cagr, sharpe, vol))

    candidates.sort(key=lambda x: x[3], reverse=True)
    return candidates[:top_n]

def recommend_mfs(user_profile, top_n=5):
    """
    very simple MF recommender using latest NAV as a proxy, and risk_level if available.
    For a real system you would compute NAV CAGR from mf_navs table.
    """
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT scheme_code, name, category, risk_level FROM mutual_funds").fetchall()
    conn.close()

    cand = []
    for code, name, category, risk_level in rows:
        # basic risk match
        if user_profile.get("risk") == "low" and str(risk_level).lower() == "high":
            continue
        if user_profile.get("risk") == "high" and str(risk_level).lower() == "low":
            continue
        # Heuristic score: longer-term equity funds often have better NAV progression in history,
        # but here we use category weight and sample score:
        base = 1.0
        if category and "Equity" in str(category):
            base += 1.0
        if category and "Debt" in str(category):
            base += 0.2
        cand.append((code, name, category, base))
    cand.sort(key=lambda x: x[3], reverse=True)
    return cand[:top_n]
