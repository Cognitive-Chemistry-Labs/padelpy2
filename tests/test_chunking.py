"""Tests for Calculator chunk_size batching."""

from __future__ import annotations

import pandas as pd
import pytest
from padelpy2 import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Weight
from rdkit import Chem
from rdkit.Chem import AllChem


def _mols_from_smiles(smiles: list[str]) -> list:
    mols = []
    for smi in smiles:
        mol = Chem.AddHs(Chem.MolFromSmiles(smi))
        assert mol is not None
        AllChem.Compute2DCoords(mol)
        mols.append(mol)
    return mols


def test_chunk_size_must_be_positive():
    calc = Calculator([Weight])
    with pytest.raises(ValueError, match="positive integer"):
        calc(_mols_from_smiles(["CCO"]), chunk_size=0)
    with pytest.raises(ValueError, match="positive integer"):
        calc(_mols_from_smiles(["CCO"]), chunk_size=-1)


@pytest.mark.integration
def test_chunk_size_concatenates_rows_and_matches_default(test_molecules):
    cfg = PaDELConfig(threads=1)
    calc = Calculator([Weight], config=cfg)
    mols = test_molecules
    default = calc(mols)
    chunked = calc(mols, chunk_size=2)
    assert chunked.shape[0] == len(mols)
    assert "Name" not in default.columns
    assert list(chunked.columns) == list(default.columns)
    pd.testing.assert_frame_equal(
        chunked.reset_index(drop=True),
        default.reset_index(drop=True),
        check_dtype=False,
    )
