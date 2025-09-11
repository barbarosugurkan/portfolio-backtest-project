# ADR 17: Switching Financial Data Source to Manual Entry

## Status
Proposed
Date: 2025-09-11

## Context

During data validation tests for **fetch_financials.py**, I discovered that financial values for some companies deviated by up to 20% compared to official KAP (Public Disclosure Platform) reports. I investigated whether the discrepancies were due to reporting formats (e.g., consolidated vs. non-consolidated reports) but could not arrive at a clear, reliable explanation.

This led me to conclude that the İş Yatırım API (isyatirimhisse) is not a trustworthy or professional-quality source of financial data.

At this stage, I had three options:

1) Integrate with the KAP API – but this would require significant development effort to learn the API, rebuild fetch_financials.py, and handle authentication and schema transformations. There is also uncertainty whether the API would provide the exact historical and structured data I need, or if it might require a paid plan.

2) Continue with İş Yatırım (isyatirimhisse) – this would let me keep the current implementation, but the foundation would be unreliable. I would end up writing validation tests and logic around data that is fundamentally flawed, building the system on a “broken base.”

3) Switch to manual entry – stop fetching financials automatically for now, and instead enter the key data points (e.g., revenue, net income, market cap) manually into the database. This avoids the risk of propagating unreliable data and gives me control over accuracy.

## Decision

I will remove İş Yatırım (isyatirimhisse) as the financial data source and rework fetch_financials.py so that financial statements are populated manually into the database.

This allows me to move forward with testing, logging, and scoring systems on a clean and reliable foundation, without being blocked by questionable data quality or heavy upfront investment into KAP API integration.

## Consequences

- Guarantees accuracy for the financial data that I input, since it will be based directly on KAP filings.
- Allows the system to progress with validation, logging, and scoring features without delay.
- Avoids wasted effort building around an unreliable source.
- The solution is not scalable; entering data manually will be time-consuming as coverage expands.
- The system will not be fully automated for financial data collection.
- Future migration to an official or paid API will eventually be necessary.