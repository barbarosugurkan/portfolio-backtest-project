# ADR 9: Storing Cumulative, Quarterly and Trailing Twelve Months Data in Financial Table

## Status
Proposed
Date: 2025-08-31

## Context:
Normally companies report their income statement data cumulatively (3 months, 6 months, 9 months and 12 months data); however, this data is not enough for true analysis. Therefore, quarter data for understanding short term performance and trailing twelve months data for understanding yearly performance are needed.

## Decision:
It was decided to store data at three different levels with additional columns in the financials table:

- Cumulative values ​​(source data - revenue_c, net_income, etc.)

- Quarterly values ​​(revenue_q, net_income_q, etc.)
Calculated by deriving cumulative data.

- TTM values ​​(revenue_ttm, net_income_ttm, etc.)
Calculated by summing the quarterly data from the last four periods.

## Consequences:
- Flexibility will be provided in queries (cumulative, quarterly, and TTM can be used directly).
- Table size will increase (two additional columns for each item).
- There will be additional calculation steps in the data pipeline, but this cost is acceptable.