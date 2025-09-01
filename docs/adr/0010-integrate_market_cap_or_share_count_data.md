# ADR 10: How to integrate market capitalization / share count data

## Status
Proposed
Date: 2025-09-01

## Context:
At the beginning of designing ER diagrams and database I put a share count column in financials. However, isyatirimhisse (API that I fetch financials data) does not provide share count data, so I erased that column. However, when I tried to do calc_multiples.py I found out that I need either market cap or share count data to calculate ratios like pe, pb, etc. Several potential approaches were considered:

1) Use yfinance shares outstanding data and join into the financials

I attempted to pull share count history from yfinance (get_shares_full). However, the data turned out to be unreliable: in some cases the same date had multiple entries, and not every trading day was covered. This made it hard to align with my financial periods. For this reason, I decided not to rely on yfinance for share count.

2) Compute share count indirectly using EPS and net income

Since I already have EPS values in my financial dataset, dividing net income by EPS would in theory yield the average shares outstanding. However, I found that İş Yatırım (isyatirimhisse) does not provide EPS data consistently across all companies. As a result, this method was not applicable in practice.

3) Use market capitalization data from İş Yatırım and join with the price table (Chosen)

Instead of dealing with unreliable or incomplete share count data, I opted to directly fetch market capitalization values from İş Yatırım. These market cap values were then joined to my price table (which already contains daily prices from yfinance). This method is consistent, avoids gaps in the data, and directly gives me the ratio I need without separately managing share count.

## Decision:
I decided to integrate market capitalization data from İş Yatırım into my price table as the primary method. This provides stable, daily-aligned values without the inconsistencies observed in the other approaches.

## Consequences:
- Simplifies calculations of valuation ratios (e.g., P/E, P/B) since market cap is directly available.
- Reliance on İş Yatırım as the sole provider of market cap values introduces a dependency risk. If their format or availability changes, recalibration will be needed.
- Reliance on İş Yatırım as the sole provider of market cap values introduces a dependency risk. If their format or availability changes, recalibration will be needed.
