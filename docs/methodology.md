# Methodology

## Research Design

This project studies hidden duration risk in Indian target maturity debt funds using public disclosures. The central question is whether funds that appear low-risk because of high credit quality still expose investors to meaningful mark-to-market losses when interest rates rise.

## Scope

The first version of the project will focus on Indian target maturity debt mutual funds and ETFs for which the following public information can be collected:

- scheme name
- AMC/fund house
- benchmark index
- maturity date or target maturity year
- modified duration
- Macaulay duration where available
- average maturity
- yield to maturity
- expense ratio
- AUM
- portfolio credit quality
- monthly NAV history

## Main Risk Measures

### 1. Modified Duration

Modified duration measures the approximate percentage price change of a bond portfolio for a 1 percentage point change in yield.

Approximate relationship:

```text
Estimated price impact = - Modified Duration × Change in Yield
```

Example:

If a fund has modified duration of 6 years and yields rise by 1%, the approximate mark-to-market loss is:

```text
-6 × 1% = -6%
```

This does not imply default. It reflects interest-rate sensitivity.

### 2. Yield-to-Duration Compensation

The project will compare YTM with modified duration.

```text
YTM-to-duration ratio = YTM / Modified Duration
```

A lower ratio may indicate that investors are receiving less yield compensation for each unit of duration risk.

### 3. Stress-Loss Scenarios

The project will estimate simple duration-based stress losses under interest-rate shocks:

- +25 bps
- +50 bps
- +100 bps
- +150 bps
- +200 bps

Formula:

```text
Stress loss % = - Modified Duration × Yield Shock
```

Convexity is not included in the first version unless public data allows it.

### 4. NAV Volatility and Drawdown

Using NAV history, the project will calculate:

- monthly returns
- annualized volatility
- maximum drawdown
- worst monthly return
- downside-month frequency

### 5. Maturity Bucket Comparison

Funds will be grouped by target maturity bucket:

- short target maturity
- medium target maturity
- long target maturity

The project will compare whether longer-maturity funds show greater duration risk, stress-loss estimates, and NAV drawdowns.

## Data Quality Policy

Each data point must include a source ID. If a value is not available from a public factsheet or official disclosure, it should be left blank rather than guessed.

## Research Integrity Boundary

The paper will not provide fund recommendations. It will not classify any fund as suitable or unsuitable for investors. The research objective is to measure duration risk and disclosure transparency using public data.
