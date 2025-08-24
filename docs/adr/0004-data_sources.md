# ADR 4: Data sources

## Status
Proposed
Date: 2025-08-24

## Context
Different data sources have tradeoffs:
- yfinance: free, reliable for historical price data, broad coverage.
- skorKart repo: specialized, up-to-date financial statements for BIST.
Alternatives: TradingView API, manual filings (KAP), paid APIs (Bloomberg, Refinitiv).

## Decision
Use yfinance for prices and skorKart for financials as the primary combination. Keep secondary/backup options in case of API failure.

## Consequences
- Best available free sources for the project’s scope.
- Simplifies integration: one source per domain.
- Risk if source becomes unavailable.
- Possible format changes breaking scripts.