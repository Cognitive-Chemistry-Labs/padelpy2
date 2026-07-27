"""Migration helpers resembling padelpy entry points (additive; not a replacement)."""

from __future__ import annotations

from collections.abc import Iterable
from os import PathLike
from typing import TYPE_CHECKING

from padelpy2._extras import require_pandas, require_rdkit
from padelpy2.calculator import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Descriptor, descriptors_2d
from padelpy2.fingerprints import Fingerprint, fingerprints

if TYPE_CHECKING:
    import pandas as pd
    from rdkit.Chem import Mol

pd = require_pandas()
Chem = require_rdkit()
from rdkit.Chem import AllChem  # noqa: E402  — after require_rdkit()

__all__ = ["from_smiles", "from_sdf", "from_mdl"]


def _catalog(
    *, descriptors: bool, fingerprints_flag: bool
) -> list[Descriptor | Fingerprint]:
    catalog: list[Descriptor | Fingerprint] = []
    if descriptors:
        catalog.extend(descriptors_2d)
    if fingerprints_flag:
        catalog.extend(fingerprints)
    if not catalog:
        raise ValueError("At least one of descriptors or fingerprints must be True.")
    return catalog


def _mols_from_smiles(smiles: str | list[str]) -> list[Mol]:
    items = [smiles] if isinstance(smiles, str) else list(smiles)
    if not items:
        raise ValueError("smiles must be a non-empty string or list.")
    mols: list[Mol] = []
    for smi in items:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            raise ValueError(f"Invalid SMILES: {smi!r}")
        mol = Chem.AddHs(mol)
        AllChem.Compute2DCoords(mol)
        mols.append(mol)
    return mols


def _mols_from_supplier(supplier: Iterable[Mol], *, label: str) -> list[Mol]:
    mols: list[Mol] = []
    for mol in supplier:
        if mol is None:
            raise ValueError(f"Failed to read a molecule from {label}.")
        mol = Chem.Mol(mol)
        if mol.GetNumConformers() == 0:
            AllChem.Compute2DCoords(mol)
        mols.append(mol)
    if not mols:
        raise ValueError(f"No molecules found in {label}.")
    return mols


def _finalize(
    df: pd.DataFrame, *, as_dict: bool, single: bool
) -> pd.DataFrame | dict | list[dict]:
    if not as_dict:
        return df
    records = df.to_dict(orient="records")
    if single:
        return records[0] if records else {}
    return records


def _run(
    mols: list[Mol],
    *,
    descriptors: bool,
    fingerprints_flag: bool,
    as_dict: bool,
    config: PaDELConfig | None,
    single: bool,
) -> pd.DataFrame | dict | list[dict]:
    calc = Calculator(
        _catalog(descriptors=descriptors, fingerprints_flag=fingerprints_flag),
        config=config,
    )
    df = calc(mols)
    return _finalize(df, as_dict=as_dict, single=single)


def from_smiles(
    smiles: str | list[str],
    *,
    descriptors: bool = True,
    fingerprints: bool = False,
    as_dict: bool = False,
    config: PaDELConfig | None = None,
) -> pd.DataFrame | dict | list[dict]:
    """
    Compute stock-JAR descriptors/fingerprints from SMILES via ``Calculator``.

    This is a migration convenience for padelpy-style call sites. Prefer staying
    on padelpy when you need a stdlib-only environment. Prefer ``Calculator``
    directly for RDKit-native workflows.

    Parameters
    ----------
    smiles : str or list of str
        One SMILES string or a list of SMILES strings.
    descriptors : bool, default True
        Include the default 2D descriptor catalog.
    fingerprints : bool, default False
        Include all fingerprint types.
    as_dict : bool, default False
        If True, return a ``dict`` (single SMILES) or ``list[dict]`` (multiple).
        Mapping shape is best-effort and may differ from padelpy ``OrderedDict``.
    config : PaDELConfig or None, optional
        Forwarded to ``Calculator``.

    Returns
    -------
    pandas.DataFrame or dict or list of dict
        DataFrame by default (``Name`` dropped).
    """

    single = isinstance(smiles, str)
    mols = _mols_from_smiles(smiles)
    return _run(
        mols,
        descriptors=descriptors,
        fingerprints_flag=fingerprints,
        as_dict=as_dict,
        config=config,
        single=single,
    )


def from_sdf(
    path: PathLike,
    *,
    descriptors: bool = True,
    fingerprints: bool = False,
    as_dict: bool = False,
    config: PaDELConfig | None = None,
) -> pd.DataFrame | dict | list[dict]:
    """
    Compute stock-JAR descriptors/fingerprints from an SDF file.

    See ``from_smiles`` for parameter semantics. Not a drop-in replacement for
    padelpy; RDKit is required.
    """

    supplier = Chem.SDMolSupplier(str(path), removeHs=False)
    mols = _mols_from_supplier(supplier, label=str(path))
    return _run(
        mols,
        descriptors=descriptors,
        fingerprints_flag=fingerprints,
        as_dict=as_dict,
        config=config,
        single=len(mols) == 1,
    )


def from_mdl(
    path: PathLike,
    *,
    descriptors: bool = True,
    fingerprints: bool = False,
    as_dict: bool = False,
    config: PaDELConfig | None = None,
) -> pd.DataFrame | dict | list[dict]:
    """
    Compute stock-JAR descriptors/fingerprints from an MDL mol file.

    See ``from_smiles`` for parameter semantics. Not a drop-in replacement for
    padelpy; RDKit is required.
    """

    mol = Chem.MolFromMolFile(str(path), removeHs=False)
    if mol is None:
        raise ValueError(f"Failed to read MDL molecule from {path}.")
    if mol.GetNumConformers() == 0:
        AllChem.Compute2DCoords(mol)
    return _run(
        [mol],
        descriptors=descriptors,
        fingerprints_flag=fingerprints,
        as_dict=as_dict,
        config=config,
        single=True,
    )
