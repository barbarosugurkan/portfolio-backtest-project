# ADR 2: Why SQLite?

## Status
Proposed
Date: 2025-08-24

## Context
The project is in early development, mostly single-user, running locally. Tradeoff: SQLite (lightweight, portable) vs PostgreSQL (robust, scalable, concurrent).

## Decision
Use **SQLite** for early development and simplicity. Consider migrating to PostgreSQL if there will be many data and automation and scalability are required.

## Consequences
- Easy setup, no server required.
- Suitable for local prototyping.
- Limited concurrency, less suited for production-scale.
- Migration cost later if project scales.