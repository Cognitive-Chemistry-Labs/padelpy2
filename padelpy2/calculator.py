from typing import Iterable, List, Union

from rdkit.Chem import Mol

from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Descriptor, Fingerprint
from padelpy2.results import PaDELResults
from padelpy2.utils import check_for_invalid_mols, count_descriptor_types, \
    create_descriptortypes_xml, remove_files, write_mols_to_tempfile, \
    write_xml_string_to_tempfile
from padelpy2.wrapper import padeldescriptor


class Calculator:
    """
    A class to compute chemical descriptors and fingerprints using
    PaDEL-Descriptor.

    Parameters
    ----------
    descriptors : Iterable[Union[Descriptor, Fingerprint]]
        An iterable of Descriptor or Fingerprint objects.
    config : Union[PaDELConfig, None], optional
        Configuration for PaDEL. If None, a default configuration is used
        (default=None).

    Attributes
    ----------
    config : PaDELConfig
        The configuration settings for PaDEL.
    xml : str
        An XML string representing the descriptor types to be computed.
    n_2d : int
        Number of 2D descriptors.
    n_3d : int
        Number of 3D descriptors.
    n_fp : int
        Number of fingerprints.
    """

    def __init__(
            self,
            descriptors: Iterable[Union[Descriptor, Fingerprint]],
            config: Union[PaDELConfig, None] = None
         ):

        if config is None:
            config = PaDELConfig()
        self.config = config

        self.xml = create_descriptortypes_xml(descriptors)
        self.n_2d, self.n_3d, self.n_fp = count_descriptor_types(descriptors)

    def __call__(self, mols: List[Mol]) -> PaDELResults:
        """
        Calculates descriptors and/or fingerprints for a list of RDKit Mol
        objects.

        Parameters
        ----------
        mols : List[Mol]
            A list of RDKit Mol objects.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the computed descriptors and/or
            fingerprints.
        """

        xml_file_name = write_xml_string_to_tempfile(self.xml)
        check_for_invalid_mols(mols, True if self.n_3d > 0 else False)
        sd_file_name = write_mols_to_tempfile(mols)

        results_file_name = padeldescriptor(
            maxruntime=self.config.maxruntime,
            waitingjobs=self.config.waitingjobs,
            threads=self.config.threads,
            d_2d=True if self.n_2d > 0 else False,
            d_3d=True if self.n_3d > 0 else False,
            config=self.config.config,
            convert3d=self.config.convert3d,
            descriptortypes=xml_file_name,
            detectaromaticity=self.config.detectaromaticity,
            mol_dir=sd_file_name,
            d_file=None,
            fingerprints=True if self.n_fp > 0 else False,
            log=self.config.log,
            maxcpdperfile=self.config.maxcpdperfile,
            removesalt=self.config.removesalt,
            retain3d=self.config.retain3d,
            retainorder=self.config.retainorder,
            standardizenitro=self.config.standardizenitro,
            standardizetautomers=self.config.standardizetautomers,
            tautomerlist=self.config.tautomerlist,
            usefilenameasmolname=self.config.usefilenameasmolname,
            sp_timeout=self.config.sp_timeout,
            headless=True,
            use_tempfile=True
        )

        results = PaDELResults(results_file_name)
        remove_files(xml_file_name, sd_file_name, results_file_name)
        return results
