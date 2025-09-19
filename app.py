# app.py
# Purpose: Integrated Streamlit UI for PortfoLink - PortfoliQ + InvestMatch
import streamlit as st
import db_setup
import pandas as pd
import matplotlib.pyplot as plt

from portfolio import add_holding, calculate_portfolio, simulate_investment, get_holdings_df
from recommender import recommend_stocks, recommend_mfs

st.set_page_config(page_title="PortfoLink", layout="wide")
st.title("PortfoLink")
st.write("Portfolio tracker and personalized stock and mutual fund recommender")

tab1, tab2 = st.tabs(["PortfoliQ - Portfolio Tracker", "InvestMatch - Recommendations"])

# ------- PORTFOLIQ -------
with tab1:
    st.header("Add a holding")
    with st.form("add_hold"):
        symbol = st.text_input("Symbol, e.g. RELIANCE.NS")
        qty = st.number_input("Quantity", min_value=1.0, step=1.0, value=1.0)
        buy_price = st.number_input("Buy price per share", min_value=0.0, step=0.1, value=100.0)
        buy_date = st.text_input("Buy date YYYY-MM-DD (optional)", value="")
        submitted = st.form_submit_button("Add to portfolio")
        if submitted:
            add_holding(symbol.strip().upper(), qty, buy_price, buy_date or None)
            st.success(f"Added {qty} of {symbol}")

    st.header("Portfolio summary")
    df_port, summary = calculate_portfolio()
    if df_port is None:
        st.info("No holdings yet. Add some above.")
    else:
        st.dataframe(df_port)
        st.metric("Total Invested", summary["Total Invested"])
        st.metric("Current Value", summary["Current Value"])
        st.metric("Portfolio Return %", summary["Portfolio Return %"])
        if summary.get("Nifty 1y Return %") is not None:
            st.metric("Nifty 1y Return %", summary["Nifty 1y Return %"])

        csv = df_port.to_csv(index=False).encode('utf-8')
        st.download_button("Download portfolio CSV", csv, "portfolio.csv", "text/csv")

# ------- INVESTMATCH -------
with tab2:
    st.header("Set preferences")
    horizon = st.selectbox("Investment horizon", ["short", "medium", "long"])
    risk = st.selectbox("Risk appetite", ["low", "medium", "high"])
    sectors = st.multiselect("Preferred sectors", ["Technology", "Pharma", "Banking", "Energy", "FMCG"], default=["Technology"])
    top_n = st.slider("Number of recommendations", 3, 10, 5)

    if st.button("Get recommendations"):
        profile = {"horizon": horizon, "risk": risk, "sectors": sectors}

        # Stocks
        st.subheader("Top stock picks")
        stocks = recommend_stocks(profile, top_n=top_n)
        if stocks:
            # recommender returns tuples (symbol, name, sector, score, cagr, sharpe, vol)
            df_s = pd.DataFrame(stocks, columns=["Symbol", "Name", "Sector", "Score", "CAGR", "Sharpe", "Volatility"])
            # convert CAGR and Volatility to percent for display
            df_s["CAGR (%)"] = (df_s["CAGR"] * 100).round(2)
            df_s["Volatility (%)"] = (df_s["Volatility"] * 100).round(2)
            st.dataframe(df_s[["Symbol","Name","Sector","Score","CAGR (%)","Sharpe","Volatility (%)"]])

            # Sector allocation pie
            st.subheader("Sector allocation of picks")
            counts = df_s["Sector"].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
            ax1.axis("equal")
            st.pyplot(fig1)

            # CSV download
            st.download_button("Download stock picks CSV", df_s.to_csv(index=False).encode("utf-8"), "stock_picks.csv", "text/csv")
        else:
            st.warning("No stock picks for selected filters.")

        # Mutual funds
        st.subheader("Top mutual funds")
        mfs = recommend_mfs(profile, top_n=top_n)
        if mfs:
            df_mf = pd.DataFrame(mfs, columns=["Scheme Code", "Name", "Category", "Score"])
            st.dataframe(df_mf)
            st.download_button("Download MF picks CSV", df_mf.to_csv(index=False).encode("utf-8"), "mf_picks.csv", "text/csv")
        else:
            st.warning("No mutual funds match filters.")

        # Simulator - if stocks exist, simulate equal allocation
        st.subheader("Quick simulator - invest in picks")
        invest_amount = st.number_input("Total invest amount (INR)", min_value=1000.0, step=1000.0, value=100000.0)
        if st.button("Simulate investment"):
            sim = simulate_investment(stocks, invest_amount)
            if sim:
                st.metric("Expected CAGR %", sim["expected_cagr_pct"])
                st.metric("Expected Volatility %", sim["expected_vol_pct"])
                alloc_df = pd.DataFrame(sim["allocations"], columns=["Symbol","Allocation (INR)","CAGR (%)","Volatility (%)"])
                st.dataframe(alloc_df)
            else:
                st.warning("Simulation could not run, not enough data.")
