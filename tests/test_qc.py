"""Unit tests for padelpy2.qc (synthetic DataFrames only)."""

import math

import pandas as pd
import pytest
from padelpy2.qc import DescriptorQCReport, summarize_descriptor_frame


def test_qc_not_in_toplevel_all():
    import padelpy2

    assert "summarize_descriptor_frame" not in padelpy2.__all__
    assert not hasattr(padelpy2, "summarize_descriptor_frame")


def test_summarize_nan_constant_and_inf():
    df = pd.DataFrame(
        {
            "a": [1.0, 1.0, 1.0],
            "b": [1.0, 2.0, math.nan],
            "c": [math.nan, math.nan, math.nan],
            "d": [1.0, math.inf, 2.0],
            "e": ["x", "y", "z"],  # coerced to NaN
        }
    )
    report = summarize_descriptor_frame(df)
    assert isinstance(report, DescriptorQCReport)
    assert report.n_rows == 3
    assert report.n_cols == 5
    assert report.nan_fraction["a"] == 0.0
    assert report.nan_fraction["b"] == pytest.approx(1.0 / 3.0)
    assert report.nan_fraction["c"] == 1.0
    assert report.nan_fraction["e"] == 1.0
    assert "a" in report.constant_columns
    assert "c" in report.constant_columns
    assert "e" in report.constant_columns
    assert "b" not in report.constant_columns
    assert "d" in report.non_finite_columns
    assert "a" not in report.non_finite_columns


def test_empty_dataframe():
    df = pd.DataFrame(columns=["a", "b"])
    report = summarize_descriptor_frame(df)
    assert report.n_rows == 0
    assert report.n_cols == 2
    assert report.nan_fraction == {"a": 0.0, "b": 0.0}
    assert report.constant_columns == ()
    assert report.non_finite_columns == ()
