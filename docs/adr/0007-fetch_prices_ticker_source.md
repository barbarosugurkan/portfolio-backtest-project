# ADR 7: How to take ticker data?

## Status
Proposed
Date: 2025-08-28

## Context
In the fetch_prices.py document, there are some ways to take ticker data so that yfinance knows which ticker to take. 
1. Store tickers in a python dictionary
2. Query the database each time
3. Store tickers in a csv file

## Decision
Store tickers in a python dictionary

## Consequences
- Simple way to do such a job.
- Higher performance, less workload.
- Might have some missing data.
- Need to update the dictionary as there are more tickers.