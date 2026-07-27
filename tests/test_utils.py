"""Unit tests for padelpy2.utils helpers."""

from pathlib import Path
from subprocess import TimeoutExpired
from unittest.mock import MagicMock, patch
from xml.etree import ElementTree as ET

import pytest
from padelpy2.descriptors import Autocorrelation3D, Weight
from padelpy2.fingerprints import MACCSFingerprinter
from padelpy2.utils import (
    check_for_invalid_mols,
    count_descriptor_types,
    create_descriptortypes_xml,
    popen_timeout,
    remove_files,
    write_mols_to_tempfile,
    write_xml_string_to_tempfile,
)
from rdkit import Chem
from rdkit.Chem import rdDepictor


def test_count_descriptor_types_mixed():
    n_2d, n_3d, n_fp = count_descriptor_types(
        [Weight, Autocorrelation3D, MACCSFingerprinter]
    )
    assert (n_2d, n_3d, n_fp) == (1, 1, 1)


def test_create_descriptortypes_xml_groups():
    xml = create_descriptortypes_xml([Weight, Autocorrelation3D, MACCSFingerprinter])
    root = ET.fromstring(xml)
    groups = {g.get("name"): g for g in root.findall("Group")}
    assert set(groups) == {"2D", "3D", "Fingerprint"}
    assert groups["2D"].find("Descriptor").get("name") == "Weight"
    assert groups["3D"].find("Descriptor").get("name") == "Autocorrelation3D"
    assert groups["Fingerprint"].find("Descriptor").get("name") == (
        "MACCSFingerprinter"
    )


def test_write_and_remove_xml_tempfile():
    xml = create_descriptortypes_xml([Weight])
    path = write_xml_string_to_tempfile(xml)
    assert Path(path).is_file()
    parsed = ET.parse(path).getroot()
    assert parsed.find("Group").get("name") == "2D"
    remove_files(path)
    assert not Path(path).exists()


def test_write_mols_to_tempfile(test_molecules):
    path = write_mols_to_tempfile(test_molecules[:1])
    assert Path(path).is_file()
    assert Path(path).suffix == ".sdf"
    remove_files(path)


def test_atom_limit_raises():
    mol = Chem.MolFromSmiles("C" * 1000)
    assert mol is not None
    assert mol.GetNumAtoms() > 999
    with pytest.raises(ValueError, match=r">999 atoms"):
        check_for_invalid_mols([mol], check_3d=False)


def test_missing_3d_conformer_raises():
    mol = Chem.MolFromSmiles("CCO")
    assert mol is not None
    assert mol.GetNumConformers() == 0
    with pytest.raises(ValueError, match="without conformers"):
        check_for_invalid_mols([mol], check_3d=True)


def test_2d_check_allows_missing_conformer():
    mol = Chem.MolFromSmiles("CCO")
    assert mol is not None
    check_for_invalid_mols([mol], check_3d=False)


def test_2d_coords_fail_3d_check():
    mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
    rdDepictor.Compute2DCoords(mol)
    # 2D coords are present but Is3D() is false; 3D check must still fail.
    with pytest.raises(ValueError, match="without conformers"):
        check_for_invalid_mols([mol], check_3d=True)


def test_popen_timeout_kills_and_raises():
    mock_process = MagicMock()
    mock_process.communicate.side_effect = TimeoutExpired(
        cmd=["sleep", "99"], timeout=1
    )
    with patch("padelpy2.utils.Popen", return_value=mock_process) as mock_popen:
        with pytest.raises(TimeoutError, match="timed out after 1"):
            popen_timeout(["sleep", "99"], 1)
    mock_popen.assert_called_once()
    assert mock_popen.call_args.args[0] == ["sleep", "99"]
    mock_process.kill.assert_called_once()
