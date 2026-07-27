"""Unit tests for descriptor and fingerprint catalog metadata."""

from padelpy2.descriptors import Weight, descriptors, descriptors_2d, descriptors_3d
from padelpy2.fingerprints import MACCSFingerprinter, fingerprints


def test_weight_catalog_metadata():
    assert Weight.desc_class == "Weight"
    assert Weight.is_3d is False
    assert len(Weight.descriptors) > 0
    assert len(Weight.descriptions) == len(Weight.descriptors)
    assert all(isinstance(name, str) and name for name in Weight.descriptors)
    assert all(isinstance(text, str) and text for text in Weight.descriptions)


def test_descriptor_list_partition():
    assert len(descriptors) == len(descriptors_2d) + len(descriptors_3d)
    assert all(not d.is_3d for d in descriptors_2d)
    assert all(d.is_3d for d in descriptors_3d)
    assert Weight in descriptors_2d


def test_maccs_fingerprint_metadata():
    assert MACCSFingerprinter.fp_class == "MACCSFingerprinter"
    assert MACCSFingerprinter.n_bits == 166
    assert isinstance(MACCSFingerprinter.description, str)
    assert MACCSFingerprinter.description


def test_fingerprint_catalog_nonempty():
    assert len(fingerprints) >= 1
    assert all(fp.n_bits > 0 for fp in fingerprints)
    assert MACCSFingerprinter in fingerprints
