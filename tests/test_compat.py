"""Tests for padelpy2.compat migration helpers."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest
from padelpy2 import Calculator
from padelpy2.compat import from_mdl, from_sdf, from_smiles
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Weight
from rdkit import Chem
from rdkit.Chem import AllChem


def test_compat_not_in_toplevel_all():
    import padelpy2

    assert "from_smiles" not in padelpy2.__all__
    assert not hasattr(padelpy2, "from_smiles")


def test_calculator_call_signature_unchanged():
    import inspect

    params = inspect.signature(Calculator.__call__).parameters
    assert list(params)[:2] == ["self", "mols"]
    assert params["mols"].default is inspect.Parameter.empty


def test_from_smiles_requires_catalog():
    with pytest.raises(ValueError, match="At least one"):
        from_smiles("CCO", descriptors=False, fingerprints=False)


@pytest.mark.integration
def test_from_smiles_list_dataframe(monkeypatch):
    monkeypatch.setattr(
        "padelpy2.compat._catalog",
        lambda **_kwargs: [Weight],
    )
    df = from_smiles(
        ["CCO", "c1ccccc1"],
        config=PaDELConfig(threads=1),
    )
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, len(Weight.descriptors))
    assert "Name" not in df.columns


@pytest.mark.integration
def test_from_smiles_as_dict_single_and_list(monkeypatch):
    monkeypatch.setattr(
        "padelpy2.compat._catalog",
        lambda **_kwargs: [Weight],
    )
    one = from_smiles("CCO", as_dict=True, config=PaDELConfig(threads=1))
    many = from_smiles(["CCO", "CC(=O)O"], as_dict=True, config=PaDELConfig(threads=1))
    assert isinstance(one, dict)
    assert set(one) == set(Weight.descriptors)
    assert isinstance(many, list) and len(many) == 2
    assert all(isinstance(row, dict) for row in many)


@pytest.mark.integration
def test_from_sdf_and_mdl(monkeypatch):
    monkeypatch.setattr(
        "padelpy2.compat._catalog",
        lambda **_kwargs: [Weight],
    )
    mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    AllChem.Compute2DCoords(mol)
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        sdf_path = root / "mols.sdf"
        mdl_path = root / "mol.mol"
        writer = Chem.SDWriter(str(sdf_path))
        writer.write(mol)
        writer.write(mol)
        writer.close()
        Chem.MolToMolFile(mol, str(mdl_path))

        sdf_df = from_sdf(sdf_path, config=PaDELConfig(threads=1))
        mdl_df = from_mdl(mdl_path, config=PaDELConfig(threads=1))

    assert sdf_df.shape[0] == 2
    assert mdl_df.shape[0] == 1
    assert list(sdf_df.columns) == Weight.descriptors
