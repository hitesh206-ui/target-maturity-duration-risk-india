# Data Collection Protocol

## Objective

Collect public data for Indian target maturity debt funds in a reproducible way.

## Step 1: Identify Fund Universe

Search for Indian mutual fund schemes that include terms such as:

- Target Maturity Fund
- Target Maturity Index Fund
- Target Maturity ETF
- Bharat Bond ETF / FoF
- SDL target maturity
- G-Sec target maturity
- PSU bond target maturity

## Step 2: Inclusion Rules

Include funds if:

- The scheme has a stated target maturity year or maturity date.
- Public factsheet data are available.
- Modified duration or average maturity is disclosed.
- NAV history is available.

## Step 3: Exclusion Rules

Exclude:

- liquid funds
- overnight funds
- dynamic bond funds
- credit risk funds
- short-duration funds without target maturity
- funds with insufficient public factsheet data

## Step 4: Factsheet Variables

Collect:

- scheme name
- AMC
- benchmark
- factsheet date
- modified duration
- Macaulay duration
- average maturity
- YTM
- expense ratio
- AUM
- government/security exposure
- AAA exposure
- AA and below exposure
- cash/TREPS exposure

## Step 5: NAV Variables

Collect:

- date
- NAV
- direct/growth plan if possible
- source ID

Use the same plan consistently across schemes.

## Step 6: Source Logging

Each source must be entered in `data/documentation/source_log.csv` with:

- source ID
- source name
- source type
- source URL
- access date
- notes

## Step 7: Data Quality Rules

- Do not guess missing values.
- Do not mix direct and regular plan NAVs without labelling.
- Do not mix growth and IDCW options.
- Prefer direct-growth NAV if available and consistent.
- Record all factsheet dates.

## First Sample Target

Start with 15-30 schemes across maturity years.
