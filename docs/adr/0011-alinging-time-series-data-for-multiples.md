# ADR 11: Aligning Time-Series Data

## Status
Proposed
Date: 2025-09-02

## Context

We need to match daily stock prices with quarterly financial data to calculate valuation multiples. Our goal is to connect each day's stock price to the latest financial report available at that time. A standard merge won't work because there is no exact date match between the two datasets. The ideal solution is to use pandas' merge_asof function, which is designed for this exact problem.

## Decision

We will not use the pd.merge_asof function for now due to persistent and unresolved errors. Instead, we have decided to implement a solution using a standard pd.merge based on a calculated effective_quarter_end column. This column assumes a fixed 45-day delay for financial reports, allowing us to perform a reliable merge. We will revisit merge_asof in the future, once we have a deeper understanding of its behavior and can fully resolve the issues.

For example, all the financials for Q1 of 2025 are matched between 16 May 2025 and 14 August 2025 price data, price data between 15 August 2025 and 14 November are matched wtih financials for Q2 of 2025, and so on. Amount of delays after quarter ends are checked and 45 was an ideal number.

## Consequences

- The code is now stable and fully functional. We can proceed with our project without being blocked by complex technical errors.
- The logic is easier to understand and debug. We have a clear and predictable way to align our data.
- Our current approach relies on a fixed assumption (the 45-day delay). This means our model won't capture the real-world impact of companies that release their financial results earlier or later than 45 days. This can lead to a less accurate model, especially around earnings release dates.
- The chosen method is less efficient and flexible than a properly working merge_asof solution.

This decision prioritizes project progress and stability over perfect accuracy. It is a temporary solution that allows us to build a working model while leaving room for a more robust implementation in the future.