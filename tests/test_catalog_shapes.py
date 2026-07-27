"""Fast metadata guards for frozen default catalog column counts."""

from padelpy2 import descriptors, descriptors_2d, descriptors_3d, fingerprints
from padelpy2.descriptors import (
    AminoAcidCount,
    IPMolecularLearning,
    KierHallSmarts,
)

EXPECTED_N_2D = 1444
EXPECTED_N_3D = 431
EXPECTED_N_ALL = 1875


def _n_columns(catalog) -> int:
    return sum(len(item.descriptors) for item in catalog)


def test_default_descriptor_column_counts_from_metadata():
    assert _n_columns(descriptors_2d) == EXPECTED_N_2D
    assert _n_columns(descriptors_3d) == EXPECTED_N_3D
    assert _n_columns(descriptors) == EXPECTED_N_ALL
    assert EXPECTED_N_ALL == EXPECTED_N_2D + EXPECTED_N_3D
    assert len(descriptors) == len(descriptors_2d) + len(descriptors_3d)


def test_fingerprint_n_bits_positive():
    assert len(fingerprints) >= 1
    for fp in fingerprints:
        assert fp.n_bits > 0
        assert isinstance(fp.n_bits, int)


def test_excluded_descriptors_not_in_default_lists():
    excluded = {AminoAcidCount, IPMolecularLearning, KierHallSmarts}
    assert excluded.isdisjoint(descriptors)
    assert excluded.isdisjoint(descriptors_2d)
