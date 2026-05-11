"""Duration risk metrics for Indian target maturity debt funds."""

from __future__ import annotations

import math

import pandas as pd


def ytm_to_duration_ratio(ytm_percent: float, modified_duration: float) -> float:
    """Yield compensation per unit of modified duration."""
    if modified_duration is None or modified_duration == 0:
        return math.nan
    return float(ytm_percent) / float(modified_duration)


def stress_loss_percent(modified_duration: float, yield_shock_bps: float) -> float:
    """Estimate NAV impact from a yield shock using modified duration.

    Parameters
    ----------
    modified_duration:
        Modified duration in years.
    yield_shock_bps:
        Yield shock in basis points. Example: 100 means +1.00%.

    Returns
    -------
    float
        Approximate NAV impact in percent. Negative means loss.
    """
    shock_decimal = float(yield_shock_bps) / 10000
    return -float(modified_duration) * shock_decimal * 100


def simple_returns(nav_series: pd.Series) -> pd.Series:
    """Compute simple returns from NAV series."""
    return nav_series.astype(float).pct_change()


def annualized_volatility(returns: pd.Series, periods_per_year: int = 12) -> float:
    """Compute annualized volatility from periodic returns."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return math.nan
    return float(clean.std(ddof=1) * math.sqrt(periods_per_year))


def drawdown(nav_series: pd.Series) -> pd.Series:
    """Compute drawdown series from NAV values."""
    nav = nav_series.astype(float)
    running_max = nav.cummax()
    return nav / running_max - 1


def maximum_drawdown(nav_series: pd.Series) -> float:
    """Compute maximum drawdown from NAV series."""
    dd = drawdown(nav_series)
    if dd.dropna().empty:
        return math.nan
    return float(dd.min())


def worst_period_return(returns: pd.Series) -> float:
    """Compute worst periodic return."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return math.nan
    return float(clean.min())


def downside_month_frequency(returns: pd.Series) -> float:
    """Share of periods with negative returns."""
    clean = returns.dropna().astype(float)
    if clean.empty:
        return math.nan
    return float((clean < 0).mean())
