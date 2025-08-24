# ADR 3: Why 5 tables and normalization?

## Status
Proposed
Date: 2025-08-24

## Context
Database design requires balancing normalization (avoiding redundancy, ensuring data consistency) and denormalization (simplicity, faster reads). For financial data, multiple categories exist: companies, financials, prices, ratios, metadata.

## Decision
The schema will use 5 core tables (Companies, Financials, Prices, Ratios, Portfolio) in a normalized structure to ensure data integrity and flexibility.

## Consequences
- Consistency: avoids duplication of company and instrument data.
- Extensible: easy to add new instruments or data types later.
- Slightly more joins needed for queries.
- Potential overhead compared to a flat table for simple analytics.