# Methodology

## Research Objective

This project measures hidden duration risk in Indian target maturity debt funds using public fund disclosures.

## Core Metrics

### Modified Duration

Modified duration estimates the approximate percentage change in NAV for a 1% change in interest rates.

Approximation:

Estimated NAV Change ≈ - Modified Duration × Change in Yield

### YTM-to-Duration Ratio

Formula:

YTM / Modified Duration

This metric estimates how much yield compensation investors receive for each unit of duration risk.

### Stress Testing

Stress scenarios:

- +0.50% yield shock
- +1.00% yield shock
- +1.50% yield shock

Estimated NAV impact is calculated using modified duration.

## Sample Design

The sample includes Indian target maturity debt index funds and ETFs.

The study excludes:

- liquid funds,
- overnight funds,
- dynamic bond funds,
- credit risk funds,
- non-target-maturity debt funds.

## Data Sources

- AMC factsheets
- AMC scheme pages
- AMFI disclosure portal
- Public fund disclosures

## Limitations

- Modified duration is an approximation.
- Convexity effects are not fully incorporated.
- YTM is not a guaranteed return.
- Factsheet disclosures may vary across AMCs.
