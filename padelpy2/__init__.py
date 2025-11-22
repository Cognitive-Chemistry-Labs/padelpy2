from importlib.metadata import distribution

from padelpy2.calculator import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import descriptors, descriptors_2d, descriptors_3d
from padelpy2.fingerprints import fingerprints
from padelpy2.wrapper import padeldescriptor


__version__ = distribution("padelpy2").version
