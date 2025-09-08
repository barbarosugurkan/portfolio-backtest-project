# Test Documentation: `test_fetch_prices.py`

---

### 1. Introduction

This test suite ensures the integrity and correctness of our financial data pipeline. Its primary purpose is to verify that the `fetch_prices` function, located in `src/fetch_prices.py`, accurately fetches, processes, and prepares stock data from external sources (`yfinance` and `isyatirimhisse`) for insertion into our local database. The tests cover a wide range of scenarios, from happy-path executions to handling errors and data discrepancies.

The test suite is built using **Pytest** and **Pandas**, with the **`unittest.mock`** library used to simulate external API responses.

---

### 2. Test Structure

The test file is structured to be modular, readable, and repeatable, leveraging Pytest's powerful features.

#### Fixtures

**Fixtures** are special functions that set up a baseline for tests to run against. They are automatically managed by Pytest, ensuring each test runs in a clean, isolated environment.

* `db_conn`: This fixture creates a temporary, in-memory SQLite database connection for each test. This is crucial for isolating tests and preventing them from interfering with each other or with a real database. It guarantees that the database state is fresh for every test run, making the results highly reliable.
* `mock_yfinance_data`, `mock_is_data`, `mock_db_data`: **Mocking** is the practice of replacing real objects with controlled, fake objects. We use this to simulate data from external APIs and the database. This allows our tests to run quickly and reliably without needing an internet connection or relying on external services, which might have rate limits or downtime. Each fixture provides a pre-defined Pandas DataFrame that mimics the exact data structure we expect from each source.
* `default_params`: This fixture centralizes the common input parameters used by many tests. It reduces code duplication and makes it easy to modify test configurations in a single place.

---

### 3. Test Scenarios

Each test function is a self-contained scenario designed to validate a specific aspect of the `fetch_prices` function.

#### `test_fetch_prices_happy_path`
* **Purpose:** To verify that the function works correctly when all external data sources return valid data as expected.
* **Scenario:** Mocks provide clean data from both `yfinance` and `isyatirimhisse`. The test then asserts that the final DataFrame is in the correct format, contains the right number of rows and columns, and has the proper data types (e.g., `datetime64[ns]` for dates, `float64` for prices, and `int64` for company IDs).

#### `test_fetch_prices_when_yfinance_returns_empty`
* **Purpose:** To ensure the function handles cases where the primary data source (`yfinance`) returns an empty DataFrame without crashing.
* **Scenario:** The mock for `yfinance.download` is configured to return an empty DataFrame. The test asserts that the function gracefully handles this edge case and returns an empty DataFrame as well.

#### `test_fetch_prices_merge_mismatch`
* **Purpose:** To confirm that the merge operation correctly handles missing data from a secondary source (`isyatirimhisse`).
* **Scenario:** `yfinance` returns valid price data, but `isyatirimhisse` returns an empty DataFrame. The test verifies that the final result still contains the price data, but the `market_cap` column is populated with `NaN` values, as expected from a `left` merge.

#### `test_fetch_prices_handles_connection_error`
* **Purpose:** To ensure the function doesn't crash when an external API connection fails.
* **Scenario:** The `yfinance.download` mock is configured to raise a `ConnectionError`. The test checks that the function catches this error and returns an empty DataFrame, preventing the program from failing unexpectedly.

#### `test_partial_ticker_success_from_yfinance`
* **Purpose:** To validate that the function can correctly process a partial data set if `yfinance` only returns data for a subset of the requested tickers.
* **Scenario:** Mocks are configured to return data only for "BIMAS.IS" even though both "BIMAS.IS" and "THYAO.IS" were requested. The test asserts that the final DataFrame only contains data for "BIMAS.IS" (`company_id` 1).

#### `test_handles_duplicate_input_data`
* **Purpose:** To ensure the function correctly cleans up duplicate records that might exist in the raw input data.
* **Scenario:** A mock DataFrame is created with duplicate rows for the same date and ticker. The test verifies that the final output DataFrame contains only a single, unique record, demonstrating that the `drop_duplicates` logic is working as intended.

#### `test_large_dataset`
* **Purpose:** To test the function's performance and stability with a larger, more realistic data volume.
* **Scenario:** This test generates a large mock dataset of 100 tickers over 10 days. The primary assertion is that the function can process this large volume of data without errors, and that the resulting DataFrame has the expected columns.

#### `test_fetch_prices_handles_existing_data`
* **Purpose:** To validate the crucial upsert (update or insert) logic of the pipeline.
* **Scenario:** The test first populates the mock database with existing data. It then simulates a new data fetch that includes both