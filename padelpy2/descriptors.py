from csv import DictReader
from os.path import abspath, dirname, join


DESC_PATH = join(
    dirname(abspath(__file__)),
    "PaDEL-Descriptor",
    "descriptors.csv"
)


class Descriptor:
    """
    A class to represent a descriptor that can be used in molecular property
    calculations.

    Parameters
    ----------
    desc_class : str
        The class name of the descriptor.
    is_3d : bool
        Indicates whether the descriptor is 3D.

    Attributes
    ----------
    desc_class : str
        The class name of the descriptor.
    descriptors : list of str
        List of descriptor names associated with this class.
    descriptions : list of str
        List of descriptions for each descriptor in `descriptors`.
    is_3d : bool
        Indicates whether the descriptor is 3D.
    """

    def __init__(self, desc_class: str, is_3d: bool):

        self.desc_class = desc_class
        with open(DESC_PATH, "r") as descfile:
            reader = DictReader(descfile)
            rows = [r for r in reader if r["class"] == self.desc_class]
        self.descriptors = [r["descriptor"] for r in rows]
        self.descriptions = [r["description"] for r in rows]
        self.is_3d = is_3d


AcidicGroupCount = Descriptor("AcidicGroupCount", False)
ALOGP = Descriptor("ALOGP", False)
AminoAcidCount = Descriptor("AminoAcidCount", False)
APol  = Descriptor("APol", False)
AromaticAtomsCount = Descriptor("AromaticAtomsCount", False)
AromaticBondsCount = Descriptor("AromaticBondsCount", False)
AtomCount = Descriptor("AtomCount", False)
Autocorrelation = Descriptor("Autocorrelation", False)
BaryszMatrix = Descriptor("BaryszMatrix", False)
BasicGroupCount = Descriptor("BasicGroupCount", False)
BCUT = Descriptor("BCUT", False)
BondCount = Descriptor("BondCount", False)
BPol = Descriptor("BPol", False)
BurdenModifiedEigenvalues = Descriptor("BurdenModifiedEigenvalues", False)
CarbonTypes = Descriptor("CarbonTypes", False)
ChiChain = Descriptor("ChiChain", False)
ChiCluster = Descriptor("ChiCluster", False)
ChiPathCluster = Descriptor("ChiPathCluster", False)
ChiPath = Descriptor("ChiPath", False)
Constitutional = Descriptor("Constitutional", False)
Crippen = Descriptor("Crippen", False)
DetourMatrix = Descriptor("DetourMatrix", False)
EccentricConnectivityIndex = Descriptor("EccentricConnectivityIndex", False)
EStateAtomType = Descriptor("EStateAtomType", False)
ExtendedTopochemicalAtom = Descriptor("ExtendedTopochemicalAtom", False)
FMF = Descriptor("FMF", False)
FragmentComplexity = Descriptor("FragmentComplexity", False)
HBondAcceptorCount = Descriptor("HBondAcceptorCount", False)
HBondDonorCount = Descriptor("HBondDonorCount", False)
HybridizationRatio = Descriptor("HybridizationRatio", False)
InformationContent = Descriptor("InformationContent", False)
IPMolecularLearning = Descriptor("IPMolecularLearning", False)
KappaShapeIndices = Descriptor("KappaShapeIndices", False)
KierHallSmarts = Descriptor("KierHallSmarts", False)
LargestChain = Descriptor("LargestChain", False)
LargestPiSystem = Descriptor("LargestPiSystem", False)
LongestAliphaticChain = Descriptor("LongestAliphaticChain", False)
MannholdLogP = Descriptor("MannholdLogP", False)
McGowanVolume = Descriptor("McGowanVolume", False)
MDE = Descriptor("MDE", False)
MLFER = Descriptor("MLFER", False)
PathCount = Descriptor("PathCount", False)
PetitjeanNumber = Descriptor("PetitjeanNumber", False)
RingCount = Descriptor("RingCount", False)
RotatableBondsCount = Descriptor("RotatableBondsCount", False)
RuleOfFive = Descriptor("RuleOfFive", False)
Topological = Descriptor("Topological", False)
TopologicalCharge = Descriptor("TopologicalCharge", False)
TopologicalDistanceMatrix = Descriptor("TopologicalDistanceMatrix", False)
TPSA = Descriptor("TPSA", False)
VABC = Descriptor("VABC", False)
VAdjMa = Descriptor("VAdjMa", False)
WalkCount = Descriptor("WalkCount", False)
Weight = Descriptor("Weight", False)
WeightedPath = Descriptor("WeightedPath", False)
WienerNumbers = Descriptor("WienerNumbers", False)
XLogP = Descriptor("XLogP", False)
ZagrebIndex = Descriptor("ZagrebIndex", False)

Autocorrelation3D = Descriptor("Autocorrelation3D", True)
CPSA = Descriptor("CPSA", True)
GravitationalIndex = Descriptor("GravitationalIndex", True)
LengthOverBreadth = Descriptor("LengthOverBreadth", True)
MomentOfInertia = Descriptor("MomentOfInertia", True)
PetitjeanShapeIndex = Descriptor("PetitjeanShapeIndex", True)
RDF = Descriptor("RDF", True)
WHIM = Descriptor("WHIM", True)

descriptors = [
    ### inactivate with base PaDEL configuration
    #
    # AminoAcidCount,
    # IPMolecularLearning,
    # KierHallSmarts,
    #
    AcidicGroupCount,
    ALOGP,
    APol,
    AromaticAtomsCount,
    AromaticBondsCount,
    AtomCount,
    Autocorrelation,
    BaryszMatrix,
    BasicGroupCount,
    BCUT,
    BondCount,
    BPol,
    BurdenModifiedEigenvalues,
    CarbonTypes,
    ChiChain,
    ChiCluster,
    ChiPathCluster,
    ChiPath,
    Constitutional,
    Crippen,
    DetourMatrix,
    EccentricConnectivityIndex,
    EStateAtomType,
    ExtendedTopochemicalAtom,
    FMF,
    FragmentComplexity,
    HBondAcceptorCount,
    HBondDonorCount,
    HybridizationRatio,
    InformationContent,
    KappaShapeIndices,
    LargestChain,
    LargestPiSystem,
    LongestAliphaticChain,
    MannholdLogP,
    McGowanVolume,
    MDE,
    MLFER,
    PathCount,
    PetitjeanNumber,
    RingCount,
    RotatableBondsCount,
    RuleOfFive,
    Topological,
    TopologicalCharge,
    TopologicalDistanceMatrix,
    TPSA,
    VABC,
    VAdjMa,
    WalkCount,
    Weight,
    WeightedPath,
    WienerNumbers,
    XLogP,
    ZagrebIndex,
    Autocorrelation3D,
    CPSA,
    GravitationalIndex,
    LengthOverBreadth,
    MomentOfInertia,
    PetitjeanShapeIndex,
    RDF,
    WHIM,
]

descriptors_2d = [d for d in descriptors if not d.is_3d]

descriptors_3d = [d for d in descriptors if d.is_3d]
