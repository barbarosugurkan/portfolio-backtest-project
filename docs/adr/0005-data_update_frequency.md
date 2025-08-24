# ADR 5: Data update frequency

## Status
Proposed
Date: 2025-08-24

## Context
Price data changes daily; financials only quarterly or annually. Automating both at the same frequency would be inefficient.

## Decision
Update price scripts daily; update financials only when new reports are released.

## Consequences
- Efficient use of resources.
- Aligns with actual reporting cycles.
- Requires monitoring/reporting to detect new financials.