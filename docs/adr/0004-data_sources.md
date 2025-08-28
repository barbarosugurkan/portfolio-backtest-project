# ADR 4: Data sources

## Status
Proposed
Date: 2025-08-24
Date updated: 2025-08-28

## Context
Different data sources have tradeoffs:
- yfinance: free, reliable for historical price data, broad coverage.
- isyatirimhisse: includes all the data in İş Yatırım Web site, from financials of BIST companies to some indices.
Alternatives: TradingView API, manual filings (KAP), paid APIs (Bloomberg, Refinitiv).

## Decision
Use yfinance for prices and isyatirimhisse for financials as the primary combination. Keep secondary/backup options in case of API failure. 

## Consequences
- Best available free sources for the project’s scope.
- Simplifies integration: one source per domain.
- Risk if source becomes unavailable.
- Possible format changes breaking scripts.