"""Targeted tests for pre-release coverage gaps (Calculator / compat / init)."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd
import pytest
from padelpy2 import Calculator
from padelpy2.compat import from_mdl, from_sdf, from_smiles
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Weight
from padelpy2.fingerprints import MACCSFingerprinter
from rdkit import Chem
from rdkit.Chem import rdDepictor


def _ethanol_2d() -> Chem.Mol:
    mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    rdDepictor.Compute2DCoords(mol)
    return mol


def test_version_fallback_when_distribution_missing():
    from importlib import reload
    from importlib.metadata import PackageNotFoundError

    import padelpy2 as pkg

    with patch(
        "importlib.metadata.distribution",
        side_effect=PackageNotFoundError("padelpy2"),
    ):
        reload(pkg)
        assert pkg.__version__ == "0.1.0"
    reload(pkg)


def test_on_error_nan_all_invalid_descriptor_catalog():
    mol_bad = Chem.MolFromSmiles("CCO")  # no coords / used as invalid for 3D
    from padelpy2.descriptors import Autocorrelation3D

    calc = Calculator([Autocorrelation3D], config=PaDELConfig(threads=1))
    df = calc([mol_bad, mol_bad], on_error="nan", retain_names=True)
    assert df.shape[0] == 2
    assert "Name" in df.columns
    assert list(df["Name"]) == ["mol_0", "mol_1"]
    assert df.drop(columns=["Name"]).isna().all().all()


def test_on_error_nan_all_invalid_fingerprint_raises():
    calc = Calculator([MACCSFingerprinter], config=PaDELConfig(threads=1))
    with patch(
        "padelpy2.calculator.check_for_invalid_mols",
        side_effect=ValueError("invalid"),
    ):
        with pytest.raises(ValueError, match="could not infer columns"):
            calc([_ethanol_2d()], on_error="nan")


def test_on_error_nan_single_batch_runtime_error():
    calc = Calculator([Weight], config=PaDELConfig(threads=1))
    with patch(
        "padelpy2.calculator.padeldescriptor",
        side_effect=RuntimeError("boom"),
    ):
        df = calc([_ethanol_2d()], on_error="nan")
    assert df.shape == (1, len(Weight.descriptors))
    assert df.isna().all().all()


def test_on_error_nan_single_batch_fp_reraises_without_schema():
    calc = Calculator([MACCSFingerprinter], config=PaDELConfig(threads=1))
    with patch(
        "padelpy2.calculator.padeldescriptor",
        side_effect=RuntimeError("boom"),
    ):
        with pytest.raises(RuntimeError, match="boom"):
            calc([_ethanol_2d()], on_error="nan")


def test_align_rows_retain_names_with_and_without_engine_name():
    calc = Calculator([Weight], config=PaDELConfig(threads=1))
    columns = Weight.descriptors
    computed = pd.DataFrame(
        {"Name": ["AUTO"], **{c: [1.0] for c in columns}},
    )
    out = calc._align_rows(
        computed,
        n_total=2,
        valid_indices=[1],
        retain_names=True,
    )
    assert out.at[1, "Name"] == "AUTO"
    assert pd.isna(out.at[0, columns[0]])

    computed2 = pd.DataFrame({c: [2.0] for c in columns})
    out2 = calc._align_rows(
        computed2,
        n_total=2,
        valid_indices=[0],
        retain_names=True,
    )
    assert out2.at[0, "Name"] == "mol_0"


def test_chunked_raise_propagates():
    calc = Calculator([Weight], config=PaDELConfig(threads=1))
    with patch(
        "padelpy2.calculator.padeldescriptor",
        side_effect=RuntimeError("chunk fail"),
    ):
        with pytest.raises(RuntimeError, match="chunk fail"):
            calc([_ethanol_2d(), _ethanol_2d()], chunk_size=1, on_error="raise")


def test_chunked_first_chunk_fails_uses_catalog_schema():
    calc = Calculator([Weight], config=PaDELConfig(threads=1))
    columns = Weight.descriptors
    calls = {"n": 0}

    def flaky(**_kwargs):
        calls["n"] += 1
        from tempfile import NamedTemporaryFile

        if calls["n"] == 1:
            raise TimeoutError("first chunk")
        with NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write("Name," + ",".join(columns) + "\n")
            handle.write("AUTO," + ",".join("1.0" for _ in columns) + "\n")
            return handle.name

    with patch("padelpy2.calculator.padeldescriptor", side_effect=flaky):
        df = calc(
            [_ethanol_2d(), _ethanol_2d()],
            chunk_size=1,
            on_error="nan",
            retain_names=True,
        )
    assert df.shape[0] == 2
    assert df.iloc[0].drop(labels=["Name"]).isna().all()
    assert not df.iloc[1].drop(labels=["Name"]).isna().all()


def test_run_chunked_empty_mols_returns_empty_frame():
    calc = Calculator([Weight])
    xml = calc.xml
    from padelpy2.utils import write_xml_string_to_tempfile

    xml_path = write_xml_string_to_tempfile(xml)
    try:
        df = calc._run_chunked(
            [],
            xml_path,
            chunk_size=1,
            retain_names=False,
            on_error="raise",
        )
    finally:
        from padelpy2.utils import remove_files

        remove_files(xml_path)
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_compat_empty_smiles_and_invalid():
    with pytest.raises(ValueError, match="non-empty"):
        from_smiles([])
    with pytest.raises(ValueError, match="Invalid SMILES"):
        from_smiles("not-a-smiles")


def test_compat_catalog_descriptor_and_fingerprint_branches():
    from padelpy2 import compat as compat_mod
    from padelpy2.descriptors import descriptors_2d

    desc_only = compat_mod._catalog(descriptors=True, fingerprints_flag=False)
    assert desc_only == list(descriptors_2d)

    fp_only = compat_mod._catalog(descriptors=False, fingerprints_flag=True)
    assert len(fp_only) >= 1
    assert all(isinstance(x, type(MACCSFingerprinter)) for x in fp_only)


def test_compat_sdf_none_mol_and_empty(tmp_path):
    class EmptySupplier:
        def __iter__(self):
            return iter(())

    class NoneSupplier:
        def __iter__(self):
            yield None

    with patch("padelpy2.compat.Chem.SDMolSupplier", return_value=EmptySupplier()):
        with pytest.raises(ValueError, match="No molecules"):
            from_sdf(tmp_path / "empty.sdf")

    with patch("padelpy2.compat.Chem.SDMolSupplier", return_value=NoneSupplier()):
        with pytest.raises(ValueError, match="Failed to read"):
            from_sdf(tmp_path / "bad.sdf")


def test_compat_mdl_failures(tmp_path):
    bad = tmp_path / "bad.mol"
    bad.write_text("not a molfile")
    with pytest.raises(ValueError, match="Failed to read MDL"):
        from_mdl(bad)


@pytest.mark.integration
def test_compat_supplier_adds_2d_coords(monkeypatch):
    mol = Chem.MolFromSmiles("CCO")
    assert mol.GetNumConformers() == 0

    class Supplier:
        def __iter__(self):
            yield mol

    monkeypatch.setattr(
        "padelpy2.compat._catalog",
        lambda **_kwargs: [Weight],
    )
    with patch("padelpy2.compat.Chem.SDMolSupplier", return_value=Supplier()):
        df = from_sdf("ignored.sdf", config=PaDELConfig(threads=1))
    assert df.shape[0] == 1


@pytest.mark.integration
def test_compat_mdl_computes_2d_when_no_conformers(monkeypatch, tmp_path):
    mol = Chem.MolFromSmiles("CCO")
    path = tmp_path / "noconf.mol"
    Chem.MolToMolFile(mol, str(path))
    monkeypatch.setattr(
        "padelpy2.compat._catalog",
        lambda **_kwargs: [Weight],
    )
    real_from_mol = Chem.MolFromMolFile

    def from_mol_no_conf(p, **kwargs):
        m = real_from_mol(p, **kwargs)
        if m is not None:
            m.RemoveAllConformers()
        return m

    with patch("padelpy2.compat.Chem.MolFromMolFile", side_effect=from_mol_no_conf):
        df = from_mdl(path, config=PaDELConfig(threads=1))
    assert df.shape[0] == 1


def test_wrapper_non_headless_argv():
    from padelpy2 import wrapper as wrapper_mod

    captured = {}

    def fake_popen_timeout(argv, *_args, **_kwargs):
        captured["argv"] = argv
        return b"", b""

    with (
        patch.object(wrapper_mod, "which", return_value="/usr/bin/java"),
        patch.object(wrapper_mod, "popen_timeout", side_effect=fake_popen_timeout),
        TemporaryDirectory() as tmp,
    ):
        out = Path(tmp) / "out.csv"
        out.write_text("Name,MW\nAUTO,1.0\n")
        wrapper_mod.padeldescriptor(
            mol_dir=str(Path(tmp)),
            d_file=str(out),
            headless=False,
            use_tempfile=False,
            d_2d=True,
            fingerprints=True,
            log=True,
            removesalt=True,
            retain3d=True,
            retainorder=False,
            standardizenitro=True,
            standardizetautomers=True,
            detectaromaticity=True,
            convert3d=True,
            config="cfg.txt",
            descriptortypes="types.xml",
            tautomerlist="taut.xml",
            usefilenameasmolname=True,
        )
    assert captured["argv"][:3] == ["java", "-jar", wrapper_mod.PADEL_PATH]
    assert "-Djava.awt.headless=true" not in captured["argv"]
    assert "-2d" in captured["argv"]
    assert "-fingerprints" in captured["argv"]
