# ADR 16: Data Validation for Stock Price Data

## Status
Proposed
Date: 2025-09-08

## Context

The core function of this project relies on accurate and consistent stock price data. We're fetching data from two distinct external sources: yfinance for daily prices (open, close, high, low, volume) and isyatirimhisse for market capitalization.

These external data sources are not guaranteed to be perfect or in sync. They might contain minor discrepancies due to different data collection times, handling of corporate actions (like stock splits or dividends), or simple rounding differences. Before we use this data for backtesting or other analytical purposes, we need a reliable way to ensure its quality and consistency.

We also have a robust data ingestion pipeline (fetch_prices function) that handles data acquisition, merging, and database updates. We need to create an automated test to validate the integrity of this pipeline and the data it processes.

## Decision

We will implement a dedicated data validation test using Pytest. The test (test_data_validation) will follow a "known good" approach by comparing data fetched from our pipeline against a manually curated ground_truth dataset. This test will ensure our data is accurate within acceptable tolerance levels before it's used downstream.

The validation logic is structured as follows:

- Data Ingestion: The test will call the fetch_prices function to simulate a real-world data pull.

- Ground Truth Definition: A Pandas DataFrame (ground_truth_df) will be manually created with confirmed, accurate data points for a small set of tickers and dates.

- Data Filtering and Alignment: The data pulled from the pipeline (db_df) will be filtered to match the exact (date, company_id) pairs present in the ground_truth_df. Both DataFrames will then be sorted to ensure row-by-row consistency.

- Column-Specific Validation:

    * Prices (Open, Close, High, Low): These will be validated using NumPy's allclose method with a loose absolute tolerance (e.g., atol=0.5). This is crucial because minor price differences between data sources are common. The test will fail only if the discrepancy exceeds this tolerance.

    * Volume: We'll compare volumes with a relative tolerance (e.g., a 5% deviation). This accounts for potential differences in data sources and ensures the volume is in the correct order of magnitude.

    * Market Capitalization: Similarly, market cap will be checked with a relative tolerance (e.g., 5% deviation), as it can vary slightly between providers.

- Descriptive Error Messages: When an assertion fails, the error message will be customized to provide context. It will specify the exact company_id, date, and the numerical values causing the failure, making debugging significantly easier.

## Consequences

- Proactive Error Detection: This test will catch inconsistencies and potential bugs in the data ingestion pipeline early, before the data is used for critical analysis or model training.
- Trust in Data: By validating data from external sources, we build trust in our entire data pipeline.
- Clearer Debugging: The detailed error messages reduce the time spent on troubleshooting data discrepancies. Instead of a generic AssertionError, we get a clear statement of what went wrong, where, and by how much.
- Maintenance Overhead: The primary downside is the need for manual maintenance of the ground_truth_df. If historical data points change, the test data must be updated accordingly.