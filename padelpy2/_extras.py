"""Helpers for optional runtime dependencies (pandas / RDKit)."""

from __future__ import annotations

from typing import Any

CALC_EXTRA_HINT = 'pip install "padelpy2[calc]"'


def require_pandas() -> Any:
    """Import pandas or raise an actionable ImportError."""
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "pandas is required for DataFrame APIs (Calculator, compat, qc). "
            f"Install with: {CALC_EXTRA_HINT}"
        ) from exc
    return pd


def require_rdkit() -> Any:
    """Import rdkit.Chem or raise an actionable ImportError."""
    try:
        from rdkit import Chem
    except ImportError as exc:
        raise ImportError(
            "RDKit is required for Calculator / molecule I/O helpers. "
            f"Install with: {CALC_EXTRA_HINT} "
            "(or conda-forge rdkit plus padelpy2[pandas])."
        ) from exc
    return Chem
