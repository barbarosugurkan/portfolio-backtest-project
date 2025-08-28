# ADR 6: Why Not Automate Data Update Now?

## Status
Proposed
Date: 2025-08-24

## Context
Automation for data updating (cron jobs, schedulers) adds complexity and overhead. At early stages, focus is on manual runs to validate data pipelines.

## Decision
Postpone full automation until system is stable and validated.

## Consequences
- More control during development.
- Easier debugging.
- Manual workload for now.
- Risk of human error if updates are missed.