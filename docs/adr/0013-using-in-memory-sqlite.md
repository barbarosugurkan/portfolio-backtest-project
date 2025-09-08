# ADR 13: Using In-Memory SQLite for Testing

## Status
Proposed
Date: 2025-09-08

## Context

The main script, fetch_prices.py, connects to a database and inserts cleaned stock data for each ticker. In production, this database will be long-lived and store data for many companies over many dates. This means the code interacts heavily with SQL features such as:

- Schema creation (ensuring tables exist with correct columns and datatypes).
- Inserts and updates (adding new daily data without corrupting old records).
- Constraints (preventing duplicates for the same company-date combination).

To validate this behavior, we need tests that check how the pipeline writes to a database. However, testing directly against a production database would introduce several problems:

- It would be slow, since real databases require disk I/O and network connections.
- It would be unsafe, because test data could mix with or overwrite real production data.
- It would be hard to reset, since tests need a clean state each time.

Therefore, the testing strategy must provide a database environment that is:

- Fast, so tests can run frequently.
- Isolated, so no test affects another.
- Disposable, so it can be torn down automatically after each run.

## Decision

We chose to use SQLite in-memory databases (created with sqlite3.connect(":memory:")) for all database-related tests. These databases live only in memory, exist only for the duration of the test, and disappear when the connection is closed.

This allows every test to:

- Start with a fresh schema (tables are created at the beginning of the test).
- Insert and query data without persistence beyond the test run.
- Run quickly without any disk I/O.

## Consequences

- Tests run extremely fast because all data is stored in RAM.
- Each test starts from a clean state, avoiding cross-contamination.
- Schema and SQL logic errors are caught early in development.
- SQLite is not identical to other SQL engines (e.g., PostgreSQL, MySQL). Some behavior, such as type coercion or concurrency handling, may differ. This means that while SQLite tests are excellent for logic verification, occasional integration tests against the real production database are still needed.