from os import PathLike, remove
from subprocess import PIPE, Popen, TimeoutExpired
from tempfile import NamedTemporaryFile
from typing import Iterable, List, Tuple
from xml.etree import ElementTree as ET

from rdkit import Chem
from rdkit.Chem import Mol

from padelpy2.descriptors import Descriptor, Fingerprint


def popen_timeout(command: str, timeout: int | None) -> Tuple[str, str]:
    """
    Run a subprocess command with an optional timeout.

    Parameters
    ----------
    command : str
        The command to be executed.
    timeout : int or None
        The maximum time (in seconds) to wait for the command to complete. If
        None, there is no timeout.

    Returns
    -------
    tuple
        A tuple containing the stdout and stderr of the command.
    """

    process = Popen(command.split(), stdout=PIPE, stderr=PIPE)
    try:
        return process.communicate(timeout=timeout)
    except TimeoutExpired:
        process.kill()
        raise TimeoutError(
            f"Command '{command}' timed out after {timeout} seconds."
        )


def create_descriptortypes_xml(
        descriptors: Iterable[Descriptor | Fingerprint]
     ) -> str:
    """
    Create an XML string for descriptor types.

    This function generates an XML formatted string that specifies the types of
    2D, 3D descriptors, and fingerprints to be used in molecular descriptor/
    fingerprint calculations. The resulting XML can be used as input for PaDEL-
    Descriptor.

    Parameters
    ----------
    descriptors : Iterable[Descriptor | Fingerprint]
        An iterable containing instances of Descriptor or Fingerprint classes.
        Each instance represents a specific type of descriptor or fingerprint
        to include in the XML configuration.

    Returns
    -------
    str
        A string containing the XML representation of the specified descriptors
        and fingerprints, formatted for use with PaDEL-Descriptor.
    """

    desc_2d, desc_3d, fp = [], [], []
    for desc in descriptors:
        if type(desc) is Fingerprint:
            fp.append(desc)
        elif type(desc) is Descriptor:
            if desc.is_3d:
                desc_3d.append(desc)
            else:
                desc_2d.append(desc)
    desc_names_2d = [d.desc_class for d in desc_2d]
    desc_names_3d = [d.desc_class for d in desc_3d]
    fp_names = [f.fp_class for f in fp]
    root = ET.Element("Root")
    if len(desc_names_2d) > 0:
        group = ET.SubElement(root, "Group", name="2D")
        for desc in desc_names_2d:
            ET.SubElement(group, "Descriptor", name=desc, value="true")
    if len(desc_names_3d) > 0:
        group = ET.SubElement(root, "Group", name="3D")
        for desc in desc_names_3d:
            ET.SubElement(group, "Descriptor", name=desc, value="true")
    if len(fp_names) > 0:
        group = ET.SubElement(root, "Group", name="Fingerprint")
        for f in fp_names:
            ET.SubElement(group, "Descriptor", name=f, value="true")
    return ET.tostring(root, encoding="utf-8")


def count_descriptor_types(
        descriptors: Iterable[Descriptor | Fingerprint]
     ) -> Tuple[int, int, int]:
    """
    Count the number of 2D descriptors, 3D descriptors, and fingerprints.

    Parameters
    ----------
    descriptors : Iterable[Union[Descriptor, Fingerprint]]
        An iterable containing Descriptor and/or Fingerprint objects.

    Returns
    -------
    int
        The number of 2D descriptors.
    int
        The number of 3D descriptors.
    int
        The number of fingerprints.
    """

    n_2d, n_3d, n_fp = 0, 0, 0
    for desc in descriptors:
        if type(desc) is Fingerprint:
            n_fp += 1
        elif type(desc) is Descriptor:
            if desc.is_3d:
                n_3d += 1
            else:
                n_2d += 1
    return n_2d, n_3d, n_fp


def write_xml_string_to_tempfile(xml: str) -> str:
    """
    Write an XML string to a temporary file and return the file name.

    Parameters
    ----------
    xml : str
        The XML string to be written to a temporary file.

    Returns
    -------
    str
        The file path of the created temporary XML file.
    """

    tree = ET.ElementTree(ET.fromstring(xml))
    ET.indent(tree, space="\t", level=0)
    with NamedTemporaryFile("wb", delete=False, suffix=".xml") as xmlfile:
        tree.write(xmlfile)
        xml_file_name = xmlfile.name
    return xml_file_name


def remove_files(*paths: PathLike) -> None:
    """
    Remove files from specified paths.

    Parameters
    ----------
    *paths : PathLike
        Variable length argument list of file paths to be removed.
    """

    for path in paths:
        remove(path)


def check_for_invalid_mols(mols: List[Mol], check_3d: bool) -> None:
    """
    Check for invalid molecules in terms of atom count and 3D conformers.

    Parameters
    ----------
    mols : List[Mol]
        A list of molecule objects to be checked.
    check_3d : bool
        If True, checks whether each molecule has at least one 3D conformer.

    Raises
    ------
    ValueError
        - If any molecule has more than 999 atoms.
        - If `check_3d` is True and a molecule does not have a 3D conformer.
    """

    for mol in mols:
        if mol.GetNumAtoms() > 999:
            raise ValueError("Molecule too large (>999 atoms).")
        confs = list(mol.GetConformers())
        if not (len(confs) > 0 and confs[-1].Is3D()):
            if check_3d:
                raise ValueError(
                    "Cannot calculate 3D descriptors for a molecule without "
                    "conformers."
                )


def write_mols_to_tempfile(mols: List[Mol]) -> str:
    """
    Write a list of molecule objects to a temporary SDF file.

    Parameters
    ----------
    mols : List[Mol]
        A list of molecule objects to be written to the file. Each object
        should be an instance of the RDKit Mol class.

    Returns
    -------
    str
        The name (path) of the created temporary SDF file containing the
        molecules.
    """

    with NamedTemporaryFile("w", delete=False, suffix=".sdf") as sdffile:
        sdf_file_name = sdffile.name
    writer = Chem.SDWriter(sdf_file_name)
    for mol in mols:
        writer.write(mol)
    writer.close()
    return sdf_file_name


# def run_padel_with_config(
#         descriptortypes_file: PathLike,
#         molecules_file: PathLike,
#         config: PaDELConfig,
#         d_2d: bool,
#         d_3d: bool,
#         fp: bool
#      ) -> PathLike:
#     """
#     Run PaDEL descriptor with a specified configuration.

#     Parameters
#     ----------
#     descriptortypes_file : PathLike
#         The file path to the descriptor/fingerprint types configuration.
#     molecules_file : PathLike
#         The file path to the input molecular data.
#     config : PaDELConfig
#         Configuration object containing various parameters for the PaDEL
#         execution.
#     d_2d : bool
#         Flag indicating whether 2D descriptors should be computed.
#     d_3d : bool
#         Flag indicating whether 3D descriptors should be computed.
#     fp : bool
#         Flag indicating whether fingerprints should be computed.

#     Returns
#     -------
#     PathLike
#         The path to the descriptors file generated by PaDEL-Descriptor.
#     """

#     return padeldescriptor(
#         maxruntime=config.maxruntime,
#         waitingjobs=config.waitingjobs,
#         threads=config.threads,
#         d_2d=d_2d,
#         d_3d=d_3d,
#         config=config.config,
#         convert3d=config.convert3d,
#         descriptortypes=descriptortypes_file,
#         detectaromaticity=config.detectaromaticity,
#         mol_dir=molecules_file,
#         d_file=None,
#         fingerprints=fp,
#         log=config.log,
#         maxcpdperfile=config.maxcpdperfile,
#         removesalt=config.removesalt,
#         retain3d=config.retain3d,
#         retainorder=config.retainorder,
#         standardizenitro=config.standardizenitro,
#         standardizetautomers=config.standardizetautomers,
#         tautomerlist=config.tautomerlist,
#         usefilenameasmolname=config.usefilenameasmolname,
#         sp_timeout=config.sp_timeout,
#         headless=True,
#         use_tempfile=True
#     )
