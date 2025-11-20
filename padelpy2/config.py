from dataclasses import dataclass
from os import PathLike


@dataclass
class PaDELConfig:
    """
    Configuration settings for PaDEL-Descriptor descriptor/fingerprint
    generation.

    Parameters
    ----------
    maxruntime : int, default=-1
        Maximum running time per molecule (in milliseconds). Use -1 for
        unlimited. Default is -1.
    waitingjobs : int, default=-1
        Maximum number of jobs to store in queue for worker threads to process.
        Use -1 to set it to 50*Max threads. Default is -1.
    threads : int, default=-1
        Maximum number of threads to use. Use -1 to use as many threads as the
        number of CPU cores. Default is -1.
    config : PathLike, default=None
        Configuration file. Default is None.
    convert3d : bool, default=False
        Convert molecule to 3D. Default is False.
    detectaromaticity : bool, default=False
        Remove existing aromaticity information and automatically detect
        aromaticity in the molecule before calculation of descriptors. Default
        is False.
    log : bool, default=False
        Create a log file. Name of log file is the name of the descriptors file
        with a .log extension. Default is False.
    maxcpdperfile : int, default=0
        Maximum number of compounds to be stored in each descriptor file. Use 0
        for unlimited. Default is 0.
    removesalt : bool, default=False
        Remove salt from molecule. Default is False.
    retain3d : bool, default=False
        Retain 3D coordinates when standardizing structure. However, this may
        prevent some structures from being standardized. Default is False.
    retainorder : bool, default=True
        Retain order of molecules in structural files for descriptor file. This
        may lead to large memory use if descriptor calculations are stuck at
        one molecule as the others will not be written to file and cleared from
        memory. Default is True.
    standardizenitro : bool, default=False
        Standardize nitro groups to N(:O):O. Default is False.
    standardizetautomers : bool, default=False
        Standardize tautomers. Default is False.
    tautomerlist : PathLike, default=None
        SMIRKS tautomers file. Default is None.
    usefilenameasmolname : bool, default=False
        Use filename (minus the extension) as molecule name. Default is False.
    sp_timeout : int, default=Nonea
        Timeout for subprocess execution in seconds. Default is None (no
        timeout).
    """

    maxruntime: int = -1
    waitingjobs: int = -1
    threads: int = -1
    config: PathLike = None
    convert3d: bool = False
    detectaromaticity: bool = False
    log: bool = False
    maxcpdperfile: int = 0
    removesalt: bool = False
    retain3d: bool = False
    retainorder: bool = True
    standardizenitro: bool = False
    standardizetautomers: bool = False
    tautomerlist: PathLike = None
    usefilenameasmolname: bool = False
    sp_timeout: int = None
