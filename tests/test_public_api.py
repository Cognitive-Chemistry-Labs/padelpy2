"""Smoke tests for the frozen public API surface."""

from importlib import import_module

import padelpy2
from padelpy2.descriptors import Descriptor, Weight, descriptors_2d
from padelpy2.fingerprints import Fingerprint, MACCSFingerprinter


def test_package_version_is_nonempty_string():
    assert isinstance(padelpy2.__version__, str)
    assert padelpy2.__version__


def test_toplevel_all_matches_frozen_exports():
    expected = {
        "Calculator",
        "PaDELConfig",
        "__version__",
        "descriptors",
        "descriptors_2d",
        "descriptors_3d",
        "fingerprints",
        "padeldescriptor",
    }
    assert set(padelpy2.__all__) == expected
    for name in expected:
        assert hasattr(padelpy2, name)


def test_submodule_all_declarations():
    # Top-level re-exports overwrite padelpy2.descriptors / .fingerprints with
    # lists; load submodules by absolute name so __all__ is still reachable.
    calculator = import_module("padelpy2.calculator")
    config = import_module("padelpy2.config")
    descriptors_mod = import_module("padelpy2.descriptors")
    fingerprints_mod = import_module("padelpy2.fingerprints")
    utils = import_module("padelpy2.utils")
    wrapper = import_module("padelpy2.wrapper")

    assert calculator.__all__ == ["Calculator"]
    assert config.__all__ == ["PaDELConfig"]
    assert set(descriptors_mod.__all__) == {
        "Descriptor",
        "descriptors",
        "descriptors_2d",
        "descriptors_3d",
    }
    assert set(fingerprints_mod.__all__) == {"Fingerprint", "fingerprints"}
    assert set(wrapper.__all__) == {"PADEL_PATH", "padeldescriptor"}
    assert utils.__all__ == []


def test_catalog_singletons_remain_importable():
    assert isinstance(Weight, Descriptor)
    assert isinstance(MACCSFingerprinter, Fingerprint)
    assert all(isinstance(d, Descriptor) for d in descriptors_2d)
