# ADR 1: Use Pandas for Data Processing

## Status
Proposed
Date: 2025-08-24

## Context
The project involves collecting, cleaning, and processing large sets of financial data (price data, financial statements, ratios). This data will later be stored in a relational database (SQLite/PostgreSQL) and used for analysis and scoring models. Before insertion into the database, data needs to be validated, cleaned, and transformed into consistent formats.
Alternatives: SQLAlchemy, CSV

## Decision
We will use Pandas as the main data processing layer before data is inserted into the database.

## Consequences
- Simplifies cleaning, validation, and transformation workflows.
- Reduces code complexity compared to pure Python data structures.
- Facilitates future extension to machine learning workflows.
- Additional memory usage for very large datasets (but acceptable for current project scale).
- Slight learning curve for advanced operations.