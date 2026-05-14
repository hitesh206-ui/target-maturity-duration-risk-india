# SSRN Submission Checklist - Target Maturity Duration Risk Paper

## Final title

Disclosed Duration and Realized NAV Risk in Indian Target Maturity Debt Funds: A Public-Data Pilot Study of Target Maturity Funds, Stress Loss, and Proxy Yield Sensitivity

## SSRN abstract

This paper develops a public-data framework for evaluating disclosed duration and realized NAV risk in Indian target maturity debt funds. The study combines factsheet-reported modified duration, AMFI daily NAV histories, manually downloaded Indian government yield proxies, and reproducible Python outputs to examine three questions. First, do higher disclosed durations correspond to higher realized NAV volatility and drawdown? Second, how large are first-order stress losses under parallel yield shocks of 25-200 basis points? Third, do daily NAV returns display measurable sensitivity to daily changes in matched Indian government yield proxies? The pilot sample contains eight target maturity funds and ETFs spanning 2026, 2027, 2030, and 2031 maturity buckets. The results show that disclosed modified duration is strongly associated with NAV risk in rank terms: Spearman rho is approximately 0.80 for annualized NAV volatility and absolute maximum drawdown. First-order duration stress indicates estimated losses of -4.58% for the longest-duration fund under a +100 basis point yield shock and -9.16% under a +200 basis point shock. Proxy realized-duration regressions produce positive duration estimates for seven funds, with the strongest explanatory power for the ICICI Prudential Nifty G-Sec Dec 2030 Index Fund. A separate fund-structure puzzle emerges: the BHARAT Bond ETF April 2030 and BHARAT Bond FOF April 2030 report the same modified duration, but the FOF exhibits roughly twice the annualized NAV volatility and maximum drawdown of the ETF. The paper contributes a transparent, reproducible pilot framework for distinguishing disclosed duration, observed NAV risk, and proxy rate sensitivity in Indian passive debt products. It is not investment advice and should be read as a methodological working paper.

## Keywords

target maturity funds; Indian debt mutual funds; modified duration; NAV volatility; government securities; realized duration; yield risk; passive debt funds

## JEL classification

G11, G12, G14, G23, C58

## Recommended SSRN category

Finance / Investments / Mutual Funds / Fixed Income / Emerging Markets Finance

## Final checks

- Title and abstract use pilot/public-data/proxy/methodological language.
- Main analysis avoids investment recommendations.
- F005 missing YTM is footnoted instead of guessed.
- F007 regression exclusion is explained.
- Regression language uses proxy realized duration, not exact key-rate duration.
- Figures should be regenerated from the latest workflow before any new upload.
- README has been updated to match the current working-paper framing.

## Future upgrades after SSRN upload

- Expand sample beyond eight funds.
- Add official CCIL/RBI zero-coupon curve data.
- Estimate key-rate duration across multiple tenors.
- Add more ETF/FOF matched pairs.
- Add convexity-adjusted stress tests if fund-level convexity becomes available.
