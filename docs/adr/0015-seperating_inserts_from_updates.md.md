# ADR 15: Separating Inserts from Updates

## Status
Proposed
Date: 2025-09-08

## Context

Our project fetches stock price data from multiple sources (Yahoo Finance for OHLCV data and İş Yatırım for market capitalization). This data needs to be stored in a SQLite database for further analysis, backtesting, and reporting.

A key challenge arises when handling newly fetched data:

1. Some of the records are completely new (future trading days not yet in the database).
2. Some of the records are already in the database but may have changed (e.g., adjusted closing prices, revised market cap values, or late-reported trading volumes).

If we insert everything blindly:

* We risk duplicating rows for the same company_id and date.

If we overwrite the entire table (if_exists="replace"):

* We lose historical records and disrupt downstream analytics.

If we only append (if_exists="append") without checks:

* We end up with stale or inconsistent data, because updated values from providers are ignored.

We needed a mechanism to differentiate between new records and existing records that require an update.

## Decision

We decided to separate inserts and updates into two distinct paths:

* Inserts: Rows that exist in the incoming data (final_df) but not in the database (price table) are written using .to_sql(..., if_exists='append').

* Updates: Rows that exist in both places but have at least one differing value are batched into an UPDATE SQL statement using executemany.

The pipeline works as follows:

1. Fetch raw data.
2. Merge with database by (company_id, date).
3. Use the merge indicator (_merge) to identify:
 - "left_only" → New rows → Insert path.
 - "both" → Potentially changed rows → Update path (only if diffs are detected).
4. Return (new_data_df, update_list) for caller to handle separately.

## Consequences

- Data integrity is preserved: no duplicate rows, no missing updates.
- Efficient database writes: new records are appended in bulk, while updates are applied selectively.
- Traceability: warnings are logged when an update occurs, highlighting differences in values (useful for auditing data provider reliability).
- Slightly more code complexity: separating insert/update logic requires merge operations and comparison between old vs. new values.
- Scalability: this pattern will remain valid if we switch from SQLite to a more robust RDBMS (e.g., PostgreSQL).