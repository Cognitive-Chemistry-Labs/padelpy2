"""Tests for Calculator retain_names and on_error kwargs."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from padelpy2 import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Autocorrelation3D, Weight
from rdkit import Chem
from rdkit.Chem import AllChem, rdDepictor


def _ethanol_2d() -> Chem.Mol:
    mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    rdDepictor.Compute2DCoords(mol)
    return mol


def _benzene_2d() -> Chem.Mol:
    mol = Chem.AddHs(Chem.MolFromSmiles("c1ccccc1"))
    rdDepictor.Compute2DCoords(mol)
    return mol


def test_defaults_drop_name_and_fail_fast():
    calc = Calculator([Weight], config=PaDELConfig(threads=1))
    df = calc([_ethanol_2d()])
    assert "Name" not in df.columns

    calc_3d = Calculator([Autocorrelation3D], config=PaDELConfig(threads=1))
    with pytest.raises(ValueError, match="without conformers"):
        calc_3d([Chem.MolFromSmiles("CCO")])


def test_retain_names_keeps_name_column():
    calc = Calculator([Weight], config=PaDELConfig(threads=1))
    df = calc([_ethanol_2d()], retain_names=True)
    assert "Name" in df.columns
    assert len(df) == 1


def test_on_error_nan_isolates_invalid_mol():
    mol_bad = Chem.MolFromSmiles("CCO")  # no 3D conformer
    calc = Calculator([Autocorrelation3D], config=PaDELConfig(threads=1))
    mol_3d = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    assert AllChem.EmbedMolecule(mol_3d, randomSeed=0xC0FFEE) == 0

    df = calc([mol_bad, mol_3d], on_error="nan")
    assert df.shape[0] == 2
    assert df.iloc[0].isna().all()
    assert not df.iloc[1].isna().all()


def test_on_error_nan_chunk_failure_fills_nan_rows():
    mols = [_ethanol_2d(), _benzene_2d(), _ethanol_2d()]
    calc = Calculator([Weight], config=PaDELConfig(threads=1))
    columns = Weight.descriptors
    calls = {"n": 0}

    def flaky_padeldescriptor(**_kwargs):
        calls["n"] += 1
        from tempfile import NamedTemporaryFile

        if calls["n"] == 2:
            raise RuntimeError("simulated PaDEL failure")
        with NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write("Name," + ",".join(columns) + "\n")
            handle.write("AUTO_1," + ",".join("1.0" for _ in columns) + "\n")
            return handle.name

    with patch(
        "padelpy2.calculator.padeldescriptor",
        side_effect=flaky_padeldescriptor,
    ):
        df = calc(mols, chunk_size=1, on_error="nan")

    assert df.shape == (3, len(columns))
    assert not df.iloc[0].isna().all()
    assert df.iloc[1].isna().all()
    assert not df.iloc[2].isna().all()


def test_invalid_on_error_value():
    calc = Calculator([Weight])
    with pytest.raises(ValueError, match="on_error"):
        calc([_ethanol_2d()], on_error="skip")  # type: ignore[arg-type]
