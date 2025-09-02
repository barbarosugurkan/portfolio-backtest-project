import sqlite3
import pandas as pd
import numpy as np
conn = sqlite3.connect("C:/Users/KULLANICI/Desktop/portfolio-backtest-project/data/database.db")

price_df = pd.read_sql_query("SELECT * FROM price", conn)
fin_df = pd.read_sql_query("SELECT * FROM financial", conn)

price_df["date"] = pd.to_datetime(price_df["date"])

price_df["effective_quarter_end"] = (price_df["date"] - pd.Timedelta(days=45)) + pd.offsets.QuarterEnd(-1)

fin_df["period_end"] = pd.to_datetime(
    fin_df["period_year"].astype(str) + "-" + fin_df["period_month"].astype(str) + "-01"
) + pd.offsets.MonthEnd(0)

fin_df = fin_df.sort_values(by=['company_id', 'period_year', 'period_month']).reset_index(drop=True)
fin_df["net_income_growth_ttm_yoy"] = (fin_df["net_income_ttm"] / fin_df.groupby('company_id')['net_income_ttm'].shift(4)) - 1

merged_df = price_df.merge(
    fin_df,
    left_on=["company_id", "effective_quarter_end"],
    right_on=["company_id", "period_end"],
    how="left"
)

merged_df = merged_df.rename(columns={"date":"date_of_price"})
merged_df["pe"] = merged_df["market_cap"] / merged_df["net_income_ttm"]
merged_df["pb"] = merged_df["market_cap"] / merged_df["equity"]
merged_df["ps"] = merged_df["market_cap"] / merged_df["revenue_ttm"]
merged_df["ev_ebitda"] = (merged_df['market_cap'] + merged_df['gross_debt'] - merged_df['cash_and_cash_equivalents']) / merged_df["ebitda_ttm"]
merged_df["dividend_yield"] = merged_df["dividend_ttm"] / merged_df["market_cap"]


merged_df["peg"] = merged_df["pe"] / merged_df["net_income_growth_ttm_yoy"] / 100


merged_df = merged_df[["company_id","date_of_price","period_year","period_month","pe","pb","ps","ev_ebitda","dividend_yield","peg"]]

merged_df.to_sql('multiple', conn, if_exists='append', index=False)
conn.close()
