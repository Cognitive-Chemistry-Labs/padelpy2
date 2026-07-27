"""Light DataFrame QC helpers (convenience / parity UX only)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from padelpy2._extras import require_pandas

if TYPE_CHECKING:
    import pandas as pd

pd = require_pandas()

__all__ = ["DescriptorQCReport", "summarize_descriptor_frame"]


@dataclass(frozen=True)
class DescriptorQCReport:
    """Summary statistics for a descriptor/fingerprint DataFrame."""

    n_rows: int
    n_cols: int
    nan_fraction: dict[str, float]
    constant_columns: tuple[str, ...]
    non_finite_columns: tuple[str, ...]


def summarize_descriptor_frame(df: pd.DataFrame) -> DescriptorQCReport:
    """
    Summarize missingness and simple column pathologies in a result frame.

    This is a convenience helper for post-calculation checks. It is not a
    uniqueness claim versus other PaDEL wrappers or general cheminformatics QC
    tools.

    Parameters
    ----------
    df : pandas.DataFrame
        Typically a ``Calculator`` result (numeric descriptor columns).

    Returns
    -------
    DescriptorQCReport
        Row/column counts, per-column NaN fractions, names of constant columns
        (including all-NaN), and columns containing ``±inf``.
    """

    n_rows, n_cols = df.shape
    nan_fraction: dict[str, float] = {}
    constant: list[str] = []
    non_finite: list[str] = []

    for col in df.columns:
        name = str(col)
        series = pd.to_numeric(df[col], errors="coerce")
        values = series.to_numpy(dtype=float, copy=False)
        if n_rows == 0:
            nan_fraction[name] = 0.0
            continue

        nan_fraction[name] = float(np.isnan(values).mean())
        non_nan = values[~np.isnan(values)]
        # All-NaN or a single distinct non-NaN value → constant.
        if non_nan.size == 0 or np.unique(non_nan).size == 1:
            constant.append(name)
        if np.isinf(values).any():
            non_finite.append(name)

    return DescriptorQCReport(
        n_rows=n_rows,
        n_cols=n_cols,
        nan_fraction=nan_fraction,
        constant_columns=tuple(constant),
        non_finite_columns=tuple(non_finite),
    )
