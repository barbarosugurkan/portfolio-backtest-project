# ADR 12: Why Pytest?

## Status
Proposed
Date: 2025-09-08

## Context

As our project grows, testing becomes increasingly important to ensure correctness, maintainability, and confidence in changes. We needed a testing framework that is:

- Widely used and actively maintained.
- Easy to integrate into Python projects without heavy configuration.
- Flexible enough to cover simple unit tests, integration tests, and data validation scenarios.
- Compatible with mocking, fixtures, and parameterized testing since our code depends on external services (e.g., Yahoo Finance, İş Yatırım APIs).

Other options like Python’s built-in unittest framework or nose were considered. However, unittest requires more boilerplate and less expressive assertions, while nose is no longer actively maintained.

Given these needs, pytest stands out as a modern, flexible, and developer-friendly testing tool.

## Decision

We decided to adopt pytest as the primary testing framework for the project. The reasons are:

- Minimal boilerplate — tests can be written as plain functions.
- Rich fixture system for reusable setup/teardown logic.
- Built-in support for parameterization.
- Cleaner and more expressive assertion handling.
- Large ecosystem of plugins and strong community support.

## Consequences

- Tests will be easier to write, read, and maintain.
- The project benefits from pytest’s ecosystem (plugins for coverage, mocking, async, etc.).
- Potential learning curve for developers used to unittest, but overall the transition is minimal.