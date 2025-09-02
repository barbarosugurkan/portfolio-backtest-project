import sqlite3
import pandas as pd
import yfinance as yf
from isyatirimhisse import fetch_stock_data
from datetime import datetime

conn = sqlite3.connect("C:/Users/KULLANICI/Desktop/portfolio-backtest-project/data/database.db")

ticker_dict = ticker_dict = {"BIMAS.IS": 1, "THYAO.IS": 2, "HTTBT.IS": 3}
tickers = list(ticker_dict.keys())
start_date = '2022-01-01'
end_date = '2025-12-31'

start_date_object = datetime.strptime(start_date, "%Y-%m-%d")
end_date_object = datetime.strptime(end_date, "%Y-%m-%d")

data = yf.download(tickers, start=start_date, end=end_date)
data.columns = ['_'.join(col).strip() for col in data.columns.values]
data = data.reset_index()
data = pd.melt(data, id_vars=['Date'], var_name='ticker_info', value_name='value')
data[['data_type', 'ticker']] = data['ticker_info'].str.split('_', expand=True)
data.drop('ticker_info', axis=1, inplace=True)

data = data.pivot_table(index=['Date', 'ticker'], columns='data_type', values='value').reset_index()
data.columns.name = None
data.columns = data.columns.str.lower()
data['company_id'] = data['ticker'].map(ticker_dict)

mc_df = fetch_stock_data(
    symbols=[s[:-3] for s in tickers],
    start_date=start_date_object.strftime("%d-%m-%Y"),
    end_date=end_date_object.strftime("%d-%m-%Y"),
    save_to_excel=False
)
mc_df = mc_df[["HGDG_HS_KODU","HGDG_TARIH","PD"]]
mc_df = mc_df.rename(columns={"HGDG_HS_KODU": "ticker", "HGDG_TARIH": "date","PD":"market_cap"})
mc_df["ticker"] = mc_df["ticker"] + ".IS"
data = data.merge(
    mc_df,
    how="left",
    left_on=["ticker", "date"],
    right_on=["ticker", "date"]
)
data.drop('ticker', axis=1, inplace=True)

data.to_sql('price', conn, if_exists='append', index=False)
conn.close()