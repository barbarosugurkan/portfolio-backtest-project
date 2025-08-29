import pandas as pd
import numpy as np
import sqlite3
from isyatirimhisse import fetch_financials

conn = sqlite3.connect("C:/Users/KULLANICI/Desktop/portfolio-backtest-project/data/database.db")

ticker_dict = {"THYAO":2,"BIMAS":1}

df = fetch_financials(
    symbols=list(ticker_dict.keys()),
    start_year=2025,
    end_year=2025,
    exchange="TRY",
    financial_group='1',
    save_to_excel=False
)

df.drop(['FINANCIAL_ITEM_NAME_TR',"FINANCIAL_ITEM_CODE"], axis=1, inplace=True)  

df_melted = df.melt(
    id_vars=['FINANCIAL_ITEM_NAME_EN', 'SYMBOL'],
    var_name='Period',
    value_name='Value'
)

df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')

df_pivoted = df_melted.pivot_table(
    index=['SYMBOL', 'Period'],
    columns='FINANCIAL_ITEM_NAME_EN',
    values='Value'
).reset_index()
df_pivoted.columns.name = None
df_pivoted.columns = df_pivoted.columns.str.lower().str.replace(" ","_")
df_pivoted = df_pivoted.rename(columns={'net_sales': 'revenue',"gross_profit_(loss)": "gross_profit","operating_profits":"operating_profit","net_profit_after_taxes":"net_income","long_term_liabilities":"long_term_debt","short_term_liabilities":"short_term_debt","shareholders_equity":"equity"})
df_pivoted['ebitda'] = (df_pivoted['gross_profit'] - 
               df_pivoted['marketing_selling_&_distrib._expenses_(-)'].abs() -
               df_pivoted['general_administrative_expenses_(-)'].abs() - 
               df_pivoted['research_&_development_expenses_(-)'].abs() +
               df_pivoted['depreciation_&_amortization'])
df_pivoted['fixed_assets'] = df_pivoted['total_assets'] - df_pivoted['current_assets']
df_pivoted['gross_debt'] = (
    df_pivoted['short-term_financial_loans'] + 
    df_pivoted['long-term_financial_loans'] + 
    df_pivoted['other_short-term_financial_liabilities'] +
    df_pivoted['short-term_loans_from_financial_operations'] + 
    df_pivoted['long-term_loans_from_financial_operations']
)
df_pivoted['net_debt'] = df_pivoted['gross_debt'] - df_pivoted["cash\xa0and\xa0cash\xa0equivalents"] - df_pivoted['short-term_financial_investments']
df_pivoted['company_id'] = df_pivoted['symbol'].map(ticker_dict)
df_pivoted["date_of_publish"] = np.nan

df_pivoted = df_pivoted[['company_id',"period","date_of_publish","revenue","gross_profit","operating_profit","ebitda","net_income","current_assets","fixed_assets","long_term_debt","short_term_debt","gross_debt","net_debt","equity"]]

df_pivoted.to_sql('financial', conn, if_exists='append', index=False)
conn.close()
