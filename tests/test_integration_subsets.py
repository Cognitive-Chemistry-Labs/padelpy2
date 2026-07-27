"""Integration tests for custom/mixed catalogs and live PaDELConfig flags."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from padelpy2 import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import (
    ALOGP,
    AromaticAtomsCount,
    AromaticBondsCount,
    Autocorrelation3D,
    Crippen,
    Weight,
)
from padelpy2.fingerprints import MACCSFingerprinter
from rdkit import Chem
from rdkit.Chem import AllChem

ORACLE_DIR = Path(__file__).resolve().parent / "fixtures" / "oracles_v1"
ORACLE_SMILES = ["CCO", "c1ccccc1", "CC(=O)O"]
ORACLE_CONFIG = PaDELConfig(threads=1)
ABS_TOL = 1e-6
REL_TOL = 1e-6


def _oracle_mols_2d() -> list:
    mols = []
    for smi in ORACLE_SMILES:
        mol = Chem.AddHs(Chem.MolFromSmiles(smi))
        assert mol is not None
        AllChem.Compute2DCoords(mol)
        mols.append(mol)
    return mols


def _benzene_2d() -> Chem.Mol:
    mol = Chem.AddHs(Chem.MolFromSmiles("c1ccccc1"))
    assert mol is not None
    AllChem.Compute2DCoords(mol)
    return mol


def _assert_frame_close(actual: pd.DataFrame, expected: pd.DataFrame) -> None:
    assert list(actual.columns) == list(expected.columns)
    assert actual.shape == expected.shape
    for col in expected.columns:
        a = pd.to_numeric(actual[col], errors="coerce")
        e = pd.to_numeric(expected[col], errors="coerce")
        assert np.allclose(
            a.to_numpy(dtype=float),
            e.to_numpy(dtype=float),
            rtol=REL_TOL,
            atol=ABS_TOL,
            equal_nan=True,
        ), f"mismatch in column {col}"


def test_custom_subset_matches_oracle():
    expected = pd.read_csv(ORACLE_DIR / "subset_2d.csv")
    actual = Calculator([ALOGP, Crippen, Weight], config=ORACLE_CONFIG)(
        _oracle_mols_2d()
    )
    assert "Name" not in actual.columns
    _assert_frame_close(actual, expected)


def test_mixed_descriptors_and_fingerprints(test_molecules):
    calc = Calculator([Weight, MACCSFingerprinter], config=ORACLE_CONFIG)
    results = calc(test_molecules)
    n_weight = len(Weight.descriptors)
    assert results.shape == (len(test_molecules), n_weight + MACCSFingerprinter.n_bits)
    assert "Name" not in results.columns
    assert list(results.columns[:n_weight]) == Weight.descriptors
    assert results.shape[1] - n_weight == 166


def test_detectaromaticity_flag_passthrough_end_to_end():
    """Live config flag: stock default keeps benzene aromatic counts at 0; flag → 6."""
    mols = [_benzene_2d()]
    descs = [AromaticAtomsCount, AromaticBondsCount]
    off = Calculator(descs, config=PaDELConfig(threads=1))(mols)
    on = Calculator(descs, config=PaDELConfig(threads=1, detectaromaticity=True))(mols)
    assert off.loc[0, "naAromAtom"] == 0
    assert off.loc[0, "nAromBond"] == 0
    assert on.loc[0, "naAromAtom"] == 6
    assert on.loc[0, "nAromBond"] == 6


def test_name_column_dropped_by_default(test_molecules):
    df = Calculator([Weight], config=ORACLE_CONFIG)(test_molecules)
    assert "Name" not in df.columns
    assert len(df.columns) == len(Weight.descriptors)


def test_fail_fast_missing_3d_does_not_return_frame():
    calc = Calculator([Autocorrelation3D], config=ORACLE_CONFIG)
    mol = Chem.MolFromSmiles("CCO")
    assert mol is not None
    with patch("padelpy2.calculator.padeldescriptor") as mocked:
        with pytest.raises(ValueError, match="without conformers"):
            calc([mol])
    mocked.assert_not_called()
