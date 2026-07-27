"""Stock-JAR golden oracle tests (G2 / oracles_v1)."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from padelpy2 import Calculator, descriptors_2d, descriptors_3d
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import ALOGP, Crippen, Weight
from padelpy2.fingerprints import MACCSFingerprinter
from padelpy2.wrapper import PADEL_PATH
from rdkit import Chem
from rdkit.Chem import AllChem

ORACLE_DIR = Path(__file__).resolve().parent / "fixtures" / "oracles_v1"
META = json.loads((ORACLE_DIR / "meta.json").read_text(encoding="utf-8"))
SENTINELS = json.loads(
    (ORACLE_DIR / "benzene_aromatic_sentinels.json").read_text(encoding="utf-8")
)
SMILES = META["smiles"]
BENZENE_ROW = META["benzene_row_index"]
EMBED_SEED = META["embed_seed"]
ABS_TOL = META["abs_tol"]
REL_TOL = META["rel_tol"]
ORACLE_CONFIG = PaDELConfig(threads=META.get("padel_threads", 1))


def _jar_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mols(*, with_3d: bool) -> list:
    mols = []
    for smi in SMILES:
        mol = Chem.MolFromSmiles(smi)
        assert mol is not None
        mol = Chem.AddHs(mol)
        if with_3d:
            status = AllChem.EmbedMolecule(mol, randomSeed=EMBED_SEED)
            assert status == 0
        else:
            AllChem.Compute2DCoords(mol)
        mols.append(mol)
    return mols


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
        ), f"oracle drift in column {col}"


def test_vendored_jar_sha256_matches_oracle_card():
    digest = _jar_sha256(Path(PADEL_PATH))
    assert digest == META["stock_jar_sha256"]
    card = (ORACLE_DIR / "DATASET_CARD.md").read_text(encoding="utf-8")
    assert META["stock_jar_sha256"] in card


def test_oracle_fixture_shapes_match_card():
    """Fixture dimensions match meta.json; live shape guards remain in test_all.py."""
    assert META["shapes"]["descriptors_2d"] == [3, 1444]
    assert META["shapes"]["descriptors_3d"] == [3, 431]
    assert META["shapes"]["maccs"] == [3, 166]
    assert META["shapes"]["subset_2d"] == [3, 7]
    assert pd.read_csv(ORACLE_DIR / "descriptors_2d.csv").shape == (3, 1444)
    assert pd.read_csv(ORACLE_DIR / "descriptors_3d.csv").shape == (3, 431)
    assert pd.read_csv(ORACLE_DIR / "maccs.csv").shape == (3, 166)


def test_subset_2d_oracle():
    expected = pd.read_csv(ORACLE_DIR / "subset_2d.csv")
    actual = Calculator([ALOGP, Crippen, Weight], config=ORACLE_CONFIG)(
        _mols(with_3d=False)
    )
    _assert_frame_close(actual, expected)


def test_descriptors_2d_oracle():
    expected = pd.read_csv(ORACLE_DIR / "descriptors_2d.csv")
    actual = Calculator(descriptors_2d, config=ORACLE_CONFIG)(_mols(with_3d=False))
    assert actual.shape == (3, 1444)
    _assert_frame_close(actual, expected)


def test_maccs_oracle():
    expected = pd.read_csv(ORACLE_DIR / "maccs.csv")
    actual = Calculator([MACCSFingerprinter], config=ORACLE_CONFIG)(
        _mols(with_3d=False)
    )
    assert actual.shape[1] == MACCSFingerprinter.n_bits
    _assert_frame_close(actual, expected)


def test_descriptors_3d_oracle():
    expected = pd.read_csv(ORACLE_DIR / "descriptors_3d.csv")
    actual = Calculator(descriptors_3d, config=ORACLE_CONFIG)(_mols(with_3d=True))
    assert actual.shape == (3, 431)
    _assert_frame_close(actual, expected)


def test_benzene_aromatic_sentinels():
    """Stock JAR pins aromatic/topology sentinel values for benzene."""
    assert SENTINELS["smiles"] == "c1ccccc1"
    assert SENTINELS["row_index"] == BENZENE_ROW
    actual = Calculator(descriptors_2d, config=ORACLE_CONFIG)(_mols(with_3d=False))
    row = actual.iloc[BENZENE_ROW]
    for col, expected in SENTINELS["columns"].items():
        got = float(row[col])
        assert np.isclose(got, expected, rtol=REL_TOL, atol=ABS_TOL), (
            f"benzene sentinel drift: {col} got {got}, expected {expected}"
        )
    # Explicit stock-JAR aromaticity contract (default config → 0 / 0).
    assert row["naAromAtom"] == 0
    assert row["nAromBond"] == 0


@pytest.mark.parametrize(
    "col,wrong",
    [("naAromAtom", 6), ("nAromBond", 6)],
)
def test_benzene_sentinel_rejects_nonzero_aromatic_counts(col, wrong):
    """Guard that oracles pin zero aromatic counts, not the common 6/6 values."""
    assert SENTINELS["columns"][col] != wrong
