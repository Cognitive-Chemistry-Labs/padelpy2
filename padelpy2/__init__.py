from __future__ import annotations

from importlib.metadata import PackageNotFoundError, distribution
from typing import TYPE_CHECKING, Any

from padelpy2.config import PaDELConfig as PaDELConfig
from padelpy2.descriptors import descriptors as descriptors
from padelpy2.descriptors import descriptors_2d as descriptors_2d
from padelpy2.descriptors import descriptors_3d as descriptors_3d
from padelpy2.fingerprints import fingerprints as fingerprints
from padelpy2.wrapper import padeldescriptor as padeldescriptor

if TYPE_CHECKING:
    from padelpy2.calculator import Calculator as Calculator

try:
    __version__ = distribution("padelpy2").version
except PackageNotFoundError:
    __version__ = "0.2.0"

__all__ = [
    "Calculator",
    "PaDELConfig",
    "__version__",
    "descriptors",
    "descriptors_2d",
    "descriptors_3d",
    "fingerprints",
    "padeldescriptor",
]


def __getattr__(name: str) -> Any:
    """Lazy-load Calculator so a minimal install need not pull pandas/RDKit."""
    if name == "Calculator":
        from padelpy2.calculator import Calculator

        return Calculator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(__all__)
