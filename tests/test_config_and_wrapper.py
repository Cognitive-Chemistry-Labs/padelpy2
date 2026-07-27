"""Unit tests for PaDELConfig forwarding and padeldescriptor error paths."""

from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pandas as pd
import pytest
from padelpy2 import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Weight
from padelpy2.wrapper import padeldescriptor
from rdkit import Chem
from rdkit.Chem import rdDepictor


def _ethanol_2d() -> Chem.Mol:
    mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    rdDepictor.Compute2DCoords(mol)
    return mol


def test_padeldescriptor_missing_java():
    with patch("padelpy2.wrapper.which", return_value=None):
        with pytest.raises(ReferenceError, match="Java JRE 6\\+ not found"):
            padeldescriptor(d_2d=True, use_tempfile=True)


def test_padeldescriptor_forwards_config_flags_to_argv():
    captured: dict[str, list[str]] = {}

    def fake_popen(argv: list[str], timeout):
        captured["argv"] = list(argv)
        return b"", b""

    config_path = "/tmp/padel.config"
    tautomer_path = "/tmp/tautomers.txt"
    spaced_mol = "/tmp/path with spaces/mols.sdf"
    spaced_types = "/tmp/path with spaces/types.xml"
    with (
        patch("padelpy2.wrapper.which", return_value="/usr/bin/java"),
        patch("padelpy2.wrapper.popen_timeout", side_effect=fake_popen),
    ):
        out = padeldescriptor(
            maxruntime=1000,
            waitingjobs=2,
            threads=4,
            d_2d=True,
            d_3d=True,
            config=config_path,
            convert3d=True,
            descriptortypes=spaced_types,
            detectaromaticity=True,
            mol_dir=spaced_mol,
            fingerprints=True,
            log=True,
            maxcpdperfile=10,
            removesalt=True,
            retain3d=True,
            retainorder=True,
            standardizenitro=True,
            standardizetautomers=True,
            tautomerlist=tautomer_path,
            usefilenameasmolname=True,
            sp_timeout=30,
            headless=True,
            use_tempfile=True,
        )

    argv = captured["argv"]
    assert argv[:3] == ["java", "-Djava.awt.headless=true", "-jar"]
    assert "-maxruntime" in argv and argv[argv.index("-maxruntime") + 1] == "1000"
    assert "-waitingjobs" in argv and argv[argv.index("-waitingjobs") + 1] == "2"
    assert "-threads" in argv and argv[argv.index("-threads") + 1] == "4"
    assert "-maxcpdperfile" in argv and argv[argv.index("-maxcpdperfile") + 1] == "10"
    assert "-2d" in argv
    assert "-3d" in argv
    assert argv[argv.index("-config") + 1] == config_path
    assert "-convert3d" in argv
    assert argv[argv.index("-descriptortypes") + 1] == spaced_types
    assert argv[argv.index("-dir") + 1] == spaced_mol
    assert "-detectaromaticity" in argv
    assert "-fingerprints" in argv
    assert "-log" in argv
    assert "-removesalt" in argv
    assert "-retain3d" in argv
    assert "-retainorder" in argv
    assert "-standardizenitro" in argv
    assert "-standardizetautomers" in argv
    assert argv[argv.index("-tautomerlist") + 1] == tautomer_path
    assert "-usefilenameasmolname" in argv
    # Paths with spaces must remain single argv elements (not split).
    assert spaced_mol in argv
    assert spaced_types in argv
    assert out is not None


def test_padeldescriptor_runtime_error_on_stderr():
    with (
        patch("padelpy2.wrapper.which", return_value="/usr/bin/java"),
        patch(
            "padelpy2.wrapper.popen_timeout",
            return_value=(b"", b"boom"),
        ),
    ):
        with pytest.raises(RuntimeError, match="PaDEL-Descriptor encountered an error"):
            padeldescriptor(d_2d=True, use_tempfile=True)


def test_calculator_forwards_padelconfig_kwargs():
    cfg = PaDELConfig(detectaromaticity=True, removesalt=True, threads=2)
    calc = Calculator([Weight], config=cfg)
    captured: dict = {}

    def fake_padeldescriptor(**kwargs):
        captured.update(kwargs)
        with NamedTemporaryFile("w", delete=False, suffix=".csv") as handle:
            handle.write("Name,MW\nmol_0,46.07\n")
            return handle.name

    with patch(
        "padelpy2.calculator.padeldescriptor",
        side_effect=fake_padeldescriptor,
    ):
        df = calc([_ethanol_2d()])

    assert captured["detectaromaticity"] is True
    assert captured["removesalt"] is True
    assert captured["threads"] == 2
    assert captured["d_2d"] is True
    assert captured["d_3d"] is False
    assert captured["fingerprints"] is False
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["MW"]
    assert len(df) == 1


def test_calculator_rejects_missing_3d_before_java():
    from padelpy2.descriptors import Autocorrelation3D

    calc = Calculator([Autocorrelation3D])
    mol = Chem.MolFromSmiles("CCO")
    with patch("padelpy2.calculator.padeldescriptor") as mocked:
        with pytest.raises(ValueError, match="without conformers"):
            calc([mol])
    mocked.assert_not_called()
