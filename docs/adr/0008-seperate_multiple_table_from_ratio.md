# ADR 8: Separate multiples table from ratio

## Status
Proposed
Date: 2025-08-28

## Context:
The ratio table originally contained both accounting-based ratios (e.g., ROE, ROA) and price-based multiples (e.g., P/E, P/B, EV/EBITDA). However, multiples depend on market prices, while accounting ratios are derived from financial statements. Every day price-based multiples change unlike accounting-based ratios, so storing them in the same table would cause excess data.

## Decision:
A new table named multiple was created to store all price-based multiples separately from accounting ratios. This table references the company table through company_id, includes a date_of_price field to align with market data, and enforces uniqueness on (company_id, date_of_price) to avoid duplicate entries.

## Consequences:
- Improves data normalization by separating fundamentally different types of ratios.
- Makes time-series queries on multiples (e.g., historical P/E trends) more efficient.
- Simplifies joining multiples with price data.
- Schema changes might be needed if new multiples are added frequently (denormalization vs. flexibility tradeoff).