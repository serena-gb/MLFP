"""Small supervised models used by controlled benchmarks."""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def fit_predict_ridge(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    alpha: float = 1.0,
) -> np.ndarray:
    """Fit a scaled Ridge regressor and return predictions."""
    model = make_pipeline(StandardScaler(), Ridge(alpha=alpha))
    model.fit(x_train, y_train)
    return model.predict(x_test)


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute benchmark metrics without raising on constant predictions."""
    rho, _ = spearmanr(y_true, y_pred)
    if np.isnan(rho):
        rho = 0.0
    rmse = mean_squared_error(y_true, y_pred) ** 0.5
    return {
        "spearman": float(rho),
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(rmse),
    }
