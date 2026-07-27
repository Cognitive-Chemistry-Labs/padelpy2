"""Live shape smokes for default catalogs (one JAR call per catalog family)."""

import pytest
from padelpy2 import (
    Calculator,
    descriptors,
    descriptors_2d,
    descriptors_3d,
    fingerprints,
)
from padelpy2.config import PaDELConfig
from padelpy2.fingerprints import MACCSFingerprinter

CFG = PaDELConfig(threads=1)


@pytest.mark.integration
def test_2d_descriptor_generation(test_molecules):
    calc = Calculator(descriptors_2d, config=CFG)
    results = calc(test_molecules)
    assert results.shape[0] == len(test_molecules)
    assert results.shape[1] == 1444


@pytest.mark.integration
def test_3d_descriptor_generation(test_molecules):
    calc = Calculator(descriptors_3d, config=CFG)
    results = calc(test_molecules)
    assert results.shape[0] == len(test_molecules)
    assert results.shape[1] == 431


@pytest.mark.integration
def test_all_descriptor_generation(test_molecules):
    calc = Calculator(descriptors, config=CFG)
    results = calc(test_molecules)
    assert results.shape[0] == len(test_molecules)
    assert results.shape[1] == 1875


@pytest.mark.integration
def test_fingerprints_maccs_live(test_molecules):
    """One live fingerprint JAR call; full n_bits coverage is metadata-only."""
    calc = Calculator([MACCSFingerprinter], config=CFG)
    results = calc(test_molecules)
    assert results.shape[0] == len(test_molecules)
    assert results.shape[1] == MACCSFingerprinter.n_bits


def test_fingerprint_catalog_n_bits_match_metadata():
    """Avoid N JVM starts (one per fingerprint type) in the default suite."""
    assert len(fingerprints) >= 1
    for fp in fingerprints:
        assert fp.n_bits > 0
        assert isinstance(fp.fp_class, str)
