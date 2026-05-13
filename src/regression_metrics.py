"""Regression utilities for empirical duration estimation."""

from __future__ import annotations

import math

import pandas as pd


def ols_beta_alpha(x: pd.Series, y: pd.Series) -> dict:
    """Estimate y = alpha + beta*x + error with basic OLS formulas.

    Parameters
    ----------
    x:
        Independent variable, e.g. daily change in matched-tenor yield in decimal form.
    y:
        Dependent variable, e.g. daily NAV return.

    Returns
    -------
    dict
        alpha, beta, r_squared, observations.
    """
    data = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    n = len(data)
    if n < 30:
        return {"alpha": math.nan, "beta": math.nan, "r_squared": math.nan, "observations": n}

    x_mean = data["x"].mean()
    y_mean = data["y"].mean()
    x_dev = data["x"] - x_mean
    y_dev = data["y"] - y_mean
    ss_x = float((x_dev**2).sum())
    if ss_x == 0:
        return {"alpha": math.nan, "beta": math.nan, "r_squared": math.nan, "observations": n}

    beta = float((x_dev * y_dev).sum() / ss_x)
    alpha = float(y_mean - beta * x_mean)
    fitted = alpha + beta * data["x"]
    resid = data["y"] - fitted
    ss_resid = float((resid**2).sum())
    ss_total = float(((data["y"] - y_mean) ** 2).sum())
    r_squared = math.nan if ss_total == 0 else 1 - ss_resid / ss_total
    return {"alpha": alpha, "beta": beta, "r_squared": r_squared, "observations": n}
