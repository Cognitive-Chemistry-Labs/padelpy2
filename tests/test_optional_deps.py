"""Optional dependency boundaries: minimal import vs Calculator extras."""

from __future__ import annotations

import subprocess
import sys

import pytest


def test_package_import_does_not_eagerly_load_calculator():
    script = """
import sys
import padelpy2
assert "padelpy2.calculator" not in sys.modules
assert callable(padelpy2.padeldescriptor)
assert padelpy2.PaDELConfig is not None
"""
    proc = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_wrapper_import_does_not_require_calculator():
    script = """
import sys
from padelpy2.wrapper import padeldescriptor, PADEL_PATH
assert callable(padeldescriptor)
assert PADEL_PATH
assert "padelpy2.calculator" not in sys.modules
"""
    proc = subprocess.run(
        [sys.executable, "-c", script],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_require_pandas_message(monkeypatch):
    import padelpy2._extras as extras

    def boom(name, *args, **kwargs):
        if name == "pandas" or name.startswith("pandas."):
            raise ImportError("blocked")
        return real_import(name, *args, **kwargs)

    real_import = __import__
    monkeypatch.setattr("builtins.__import__", boom)
    with pytest.raises(ImportError, match=r"padelpy2\[calc\]"):
        extras.require_pandas()


def test_require_rdkit_message(monkeypatch):
    import padelpy2._extras as extras

    def boom(name, *args, **kwargs):
        if name == "rdkit" or name.startswith("rdkit."):
            raise ImportError("blocked")
        return real_import(name, *args, **kwargs)

    real_import = __import__
    monkeypatch.setattr("builtins.__import__", boom)
    with pytest.raises(ImportError, match=r"padelpy2\[calc\]"):
        extras.require_rdkit()


def test_unknown_toplevel_attribute():
    import padelpy2

    with pytest.raises(AttributeError, match="no attribute"):
        _ = padelpy2.not_a_real_export  # type: ignore[attr-defined]
