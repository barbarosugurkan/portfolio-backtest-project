# ADR 14: Mocking External Services (Yahoo Finance & İş Yatırım APIs)

## Status
Proposed
Date: 2025-09-08

## Context

Our system depends on external data providers (yfinance, isyatirimhisse). Relying on live API calls in tests would cause:

- Fragile tests that fail due to internet issues or API downtime.
- Slow test runs.
- Non-deterministic results due to changing market data.

## Decision

We chose to use mocks (unittest.mock.patch) to simulate external API responses. Test data is predefined and controlled, ensuring deterministic outcomes.

## Consequences

- Tests run offline and deterministically.
- We can simulate various scenarios (happy path, missing data, connection errors).
- Mock data may diverge from real-world responses, so occasional integration tests with live APIs are still recommended.