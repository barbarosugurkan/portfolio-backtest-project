import sqlite3
import pandas as pd
import yfinance as yf
conn = sqlite3.connect("C:/Users/KULLANICI/Desktop/portfolio-backtest-project/data/database.db")

ticker_dict = {"BIMAS.IS": 1, "THYAO.IS": 2, "HTTBT.IS": 3}
tickers = list(ticker_dict.keys())

data = yf.download(tickers, start='2025-01-01', end='2025-01-08')
data.columns = ['_'.join(col).strip() for col in data.columns.values]
data = data.reset_index()
data = pd.melt(data, id_vars=['Date'], var_name='ticker_info', value_name='value')
data[['data_type', 'ticker']] = data['ticker_info'].str.split('_', expand=True)
data.drop('ticker_info', axis=1, inplace=True)

data = data.pivot_table(index=['Date', 'ticker'], columns='data_type', values='value').reset_index()
data.columns.name = None
data.columns = data.columns.str.lower()
data['company_id'] = data['ticker'].map(ticker_dict)
data.drop('ticker', axis=1, inplace=True)

data.to_sql('price', conn, if_exists='append', index=False)
conn.close()