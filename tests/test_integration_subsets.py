"""Integration tests for custom/mixed catalogs and live PaDELConfig flags."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from padelpy2 import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import (
    AromaticAtomsCount,
    AromaticBondsCount,
    Autocorrelation3D,
    Weight,
)
from padelpy2.fingerprints import MACCSFingerprinter
from rdkit import Chem
from rdkit.Chem import rdDepictor

ORACLE_CONFIG = PaDELConfig(threads=1)


def _benzene_2d() -> Chem.Mol:
    mol = Chem.AddHs(Chem.MolFromSmiles("c1ccccc1"))
    rdDepictor.Compute2DCoords(mol)
    return mol


@pytest.mark.integration
def test_mixed_descriptors_and_fingerprints(test_molecules):
    calc = Calculator([Weight, MACCSFingerprinter], config=ORACLE_CONFIG)
    results = calc(test_molecules)
    n_weight = len(Weight.descriptors)
    assert results.shape == (len(test_molecules), n_weight + MACCSFingerprinter.n_bits)
    assert "Name" not in results.columns
    assert list(results.columns[:n_weight]) == Weight.descriptors
    assert results.shape[1] - n_weight == 166


@pytest.mark.integration
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


def test_fail_fast_missing_3d_does_not_return_frame():
    calc = Calculator([Autocorrelation3D], config=ORACLE_CONFIG)
    mol = Chem.MolFromSmiles("CCO")
    assert mol is not None
    with patch("padelpy2.calculator.padeldescriptor") as mocked:
        with pytest.raises(ValueError, match="without conformers"):
            calc([mol])
    mocked.assert_not_called()
