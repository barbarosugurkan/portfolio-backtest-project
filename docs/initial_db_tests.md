# Validation Rules & Testing of Database in SQL

- Test: **UNIQUE constraint on ticker**

SQL: INSERT INTO company (ticker, company_name, sector, created_at)
     VALUES ('BIMAS.IS', 'Duplicate Bim', 'Retail', DATE('now'));

Result: UNIQUE constraint failed: company.ticker

Conclusion: UNIQUE constraint works as expected.


- Test: **NOT NULL constraint on company_name**

SQL: INSERT INTO company (ticker, company_name, sector, created_at)
     VALUES ('XYZ.IS', NULL, 'Retail', DATE('now'));

Result: NOT NULL constraint failed: company.company_name

Conclusion: NOT NULL constraint works as expected.


- Test: **Insert valid row**

SQL: INSERT INTO company (ticker, company_name, sector, created_at)
     VALUES ('ASELS.IS', 'Aselsan A.Ş.', 'Defense', DATE('now'));

Result: 1 row inserted successfully.

Conclusion: Normal insert works as expected.


- Test: **SELECT returns expected row count**

SQL: SELECT COUNT(*) FROM company;

Result: 4 (3 from seed + 1 new insert)

Conclusion: SELECT query works and row count matches expectation.

# Tests On fetch_prices.py

- Test: **Does the script work generally?**

Script was run and database was checked from DB Browser, there were no excess or more data. Also, data was checked from TradingView for accuracy.

Conclusion: Script works and data is mostly accurate.

- Test: **Valid multiple tickers**

When we give such an input `ticker_dict = {"BIMAS.IS": 1, "THYAO.IS": 2}`, script should return price data for multiple tickers.

Result: It did return price data for multiple tickers

Conclusion: Multiple data can be taken at the same time.

- Test: **Invalid ticker**

What would happen when one ticker is valid and the other is invalid?
For example: `ticker_dict = {"BIMAS.IS": 1, "XXXXX.IS": 2}`

Result: Script gives "YFTzMissingError" but the valid data is still taken and uploaded into database.

Conclusion: The system would not fail completely when one ticker is invalid.

- Test: **Duplicate data**

Price data for 2025-01-10 was uploaded to database at max date. When the code was run such that the dates are between 2025-01-09 and 2025-01-15. How does the script react?

Result: Script gives "sqlite3.IntegrityError: UNIQUE constraint failed: price.company_id, price.date" error, which is as expected. It does not upload duplicated data; however, it also does not upload the data that is not already uploaded, too. 

Conclusion: There is no chance for duplicated data but if there is a date which would cause duplicated data the rest of the data is not uploaded.

# Tests On fetch_financials.py

- Test: **Data accuracy**

THYAO financials are checked from Fintables.

Result: revenue, gross_profit, operating_profit, net_income, current_assets, fixed_assets, long_term_debt, short_term_debt and equity data were correct but ebitda, gross_debt and net_debt calculations were wrong.

Conclusion: ebitda, gross_debt and net_debt calculations were corrected.

# Tests On calc_ratios.py

- Test: **Data accuracy**

BIMAS ratios are checked from Fintables.

Result: All were correct.

Conclusion: All were correct.