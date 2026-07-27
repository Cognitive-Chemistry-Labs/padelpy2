#!/usr/bin/env python3
"""Regenerate stock-JAR golden oracles under tests/fixtures/oracles_v1/."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from padelpy2 import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import ALOGP, Crippen, Weight, descriptors_2d, descriptors_3d
from padelpy2.fingerprints import MACCSFingerprinter
from padelpy2.wrapper import PADEL_PATH
from rdkit import Chem
from rdkit.Chem import AllChem

ROOT = Path(__file__).resolve().parents[1]
# Single-thread PaDEL avoids intermittent NaN/value flips in some 3D descriptors.
ORACLE_CONFIG = PaDELConfig(threads=1)
OUT_DIR = ROOT / "tests" / "fixtures" / "oracles_v1"

SMILES = [
    "CCO",  # ethanol
    "c1ccccc1",  # benzene (G0 aromatic divergence case)
    "CC(=O)O",  # acetic acid
]
BENZENE_ROW = 1
EMBED_SEED = 0xC0FFEE
ABS_TOL = 1e-6
REL_TOL = 1e-6

# Columns that disagreed with a peer ePaDEL bundle on benzene in G0 — pinned for drift.
AROMATIC_SENTINELS = [
    "naAromAtom",
    "nAromBond",
    "SpAbs_DzZ",
    "EE_DzZ",
    "VE1_DzZ",
    "ETA_Beta",
]


def jar_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mols_from_smiles(smiles: list[str], *, with_3d: bool) -> list:
    mols = []
    for smi in smiles:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            raise ValueError(f"invalid SMILES: {smi}")
        mol = Chem.AddHs(mol)
        if with_3d:
            status = AllChem.EmbedMolecule(mol, randomSeed=EMBED_SEED)
            if status != 0:
                raise RuntimeError(f"3D embed failed for {smi}")
        else:
            AllChem.Compute2DCoords(mol)
        mols.append(mol)
    return mols


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jar_path = Path(PADEL_PATH)
    digest = jar_sha256(jar_path)

    mols_2d = mols_from_smiles(SMILES, with_3d=False)
    mols_3d = mols_from_smiles(SMILES, with_3d=True)

    subset = Calculator([ALOGP, Crippen, Weight], config=ORACLE_CONFIG)(mols_2d)
    full_2d = Calculator(descriptors_2d, config=ORACLE_CONFIG)(mols_2d)
    maccs = Calculator([MACCSFingerprinter], config=ORACLE_CONFIG)(mols_2d)
    full_3d = Calculator(descriptors_3d, config=ORACLE_CONFIG)(mols_3d)

    subset.to_csv(OUT_DIR / "subset_2d.csv", index=False)
    full_2d.to_csv(OUT_DIR / "descriptors_2d.csv", index=False)
    maccs.to_csv(OUT_DIR / "maccs.csv", index=False)
    full_3d.to_csv(OUT_DIR / "descriptors_3d.csv", index=False)

    benzene = full_2d.iloc[BENZENE_ROW]
    sentinels = {
        "smiles": SMILES[BENZENE_ROW],
        "row_index": BENZENE_ROW,
        "columns": {col: float(benzene[col]) for col in AROMATIC_SENTINELS},
    }
    (OUT_DIR / "benzene_aromatic_sentinels.json").write_text(
        json.dumps(sentinels, indent=2) + "\n",
        encoding="utf-8",
    )

    meta = {
        "smiles": SMILES,
        "benzene_row_index": BENZENE_ROW,
        "embed_seed": EMBED_SEED,
        "padel_threads": 1,
        "abs_tol": ABS_TOL,
        "rel_tol": REL_TOL,
        "stock_jar_relpath": "padelpy2/PaDEL-Descriptor/PaDEL-Descriptor.jar",
        "stock_jar_sha256": digest,
        "shapes": {
            "subset_2d": list(subset.shape),
            "descriptors_2d": list(full_2d.shape),
            "maccs": list(maccs.shape),
            "descriptors_3d": list(full_3d.shape),
        },
    }
    (OUT_DIR / "meta.json").write_text(
        json.dumps(meta, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote oracles to {OUT_DIR}")
    print(f"stock JAR sha256: {digest}")


if __name__ == "__main__":
    main()
