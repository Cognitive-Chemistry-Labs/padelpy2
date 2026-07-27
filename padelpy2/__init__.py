from importlib.metadata import PackageNotFoundError, distribution

from padelpy2.calculator import Calculator as Calculator
from padelpy2.config import PaDELConfig as PaDELConfig
from padelpy2.descriptors import descriptors as descriptors
from padelpy2.descriptors import descriptors_2d as descriptors_2d
from padelpy2.descriptors import descriptors_3d as descriptors_3d
from padelpy2.fingerprints import fingerprints as fingerprints
from padelpy2.wrapper import padeldescriptor as padeldescriptor

try:
    __version__ = distribution("padelpy2").version
except PackageNotFoundError:
    __version__ = "0.1.0"

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
