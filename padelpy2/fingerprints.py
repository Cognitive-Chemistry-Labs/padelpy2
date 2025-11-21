from csv import DictReader
from os.path import abspath, dirname, join


FP_PATH = join(
    dirname(abspath(__file__)),
    "PaDEL-Descriptor",
    "fingerprints.csv"
)


class Fingerprint:
    """
    A class to represent a fingerprint that can be used in molecular property
    calculations.

    Parameters
    ----------
    fp_class : str
        The class name of the fingerprint.

    Attributes
    ----------
    fp_class : str
        The class name of the fingerprint.
    n_bits : int
        The number of bits for the fingerprint.
    description : str
        Description of the fingerprint.
    """

    def __init__(self, fp_class: str):

        self.fp_class = fp_class
        with open(FP_PATH, "r") as fpfile:
            reader = DictReader(fpfile)
            rows = [r for r in reader if r["class"] == self.fp_class]
        self.n_bits = int(rows[0]["bits"])
        self.description = rows[0]["description"]


Fingerprinter = Fingerprint("Fingerprinter")
ExtendedFingerprinter = Fingerprint("ExtendedFingerprinter")
EStateFingerprinter = Fingerprint("EStateFingerprinter")
GraphOnlyFingerprinter = Fingerprint("GraphOnlyFingerprinter")
MACCSFingerprinter = Fingerprint("MACCSFingerprinter")
PubchemFingerprinter = Fingerprint("PubchemFingerprinter")
SubstructureFingerprinter = Fingerprint("SubstructureFingerprinter")
SubstructureFingerprintCount = Fingerprint("SubstructureFingerprintCount")
KlekotaRothFingerprinter = Fingerprint("KlekotaRothFingerprinter")
KlekotaRothFingerprintCount = Fingerprint("KlekotaRothFingerprintCount")
AtomPairs2DFingerprinter = Fingerprint("AtomPairs2DFingerprinter")
AtomPairs2DFingerprintCount = Fingerprint("AtomPairs2DFingerprintCount")

fingerprints = [
    Fingerprinter,
    ExtendedFingerprinter,
    EStateFingerprinter,
    GraphOnlyFingerprinter,
    MACCSFingerprinter,
    PubchemFingerprinter,
    SubstructureFingerprinter,
    SubstructureFingerprintCount,
    KlekotaRothFingerprinter,
    KlekotaRothFingerprintCount,
    AtomPairs2DFingerprinter,
    AtomPairs2DFingerprintCount
]
