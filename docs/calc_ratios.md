# Document: Calculating Ratios from Financial Table

## Overview

`calc_ratios.py` is used to generate financial ratios (cumulative, quarterly, TTM) from the raw data in the financial table. This allows for direct calculation of profitability, growth, efficiency, and leverage indicators for use in investment analyses.

## 1. Debt ratios

Here are my formulas for debt ratios:

- current_ratio = `current_assetts` / `short_term_debt`
- debt_to_equity = `gross_debt` / `equity`
- debt_to_assets = `gross_debt` / `total_assets`
- debt_to_ebitda = `gross_debt` / `ebitda_ttm`

The reason why gross debt is used instead of total debt is that it shows a better view for financial risk since it only includes interest bearing debt like bank credit, bonds, etc. does not include operation debts.

## 2. Profitability ratios

There were 3 different methods for calculating profitability ratios and `net_income`, `gross_profit`, `operating_profit` are all calculated with these 3 different methods. These 3 data were divided into `revenue`.

1) Quarterly margins (_q)
This shows the instant profitability of the company. There may be seasonal fluctuations and one-time event effects.

2) Trailing twelve months margins (_ttm)
This is the mostly used margin data. It shows the last 12 month performance in stable picture. It can be used the understand how profitable the company is in the long term.

3) Cumulative (_c)
This is calculated by the financial data provided by the company. It can be used to compare how close the margins are with the year-end expectations.

## 3. Efficiency and Return ratios

- `roe` = `net_income` / `equity`
- `roa` = `net_income` / `total_assets`
- `roic` = (`operating_profit` * (1 - `effective_tax_rate`)) / `total_assets`
- `asset_turnover` = `revenue` / `total_assets`

Roe and roa ratios are calculated quarterly and trailing twelve months but roic ratio is only calculated trailing twelve months.

## 4. Growth ratios

`revenue`, `net_income` and `eps` growth are investigated by 3 different methods:

1. Trailing twelve months year over year
2. Quarterly year over year
3. Quarterly quarter over quarter

## Future Improvements:
- Add more ratios
- Sector ratios
- Control of data types
- Logging
- Solving duplicate data problem
- Making it more modular by separating it into functions.
- More data validation
