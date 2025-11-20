import io
from os import PathLike

import numpy as np
import numpy.typing as npt
import pandas
import pandas as pd


class PaDELResults:
    """
    A class to handle results from a PaDEL-Descriptor output file.

    Parameters
    ----------
    results_file : PathLike
        The path to the CSV file containing PaDEL-Descriptor results.

    Attributes
    ----------
    _results : io.StringIO
        An in-memory stream of the contents of the results.
    """

    def __init__(self, results_file: PathLike):

        with open(results_file, "r", newline="") as rfile:
            self._results = io.StringIO()
            for line in rfile:
                self._results.write(line)
            self._results.seek(0)

    def to_numpy(self) -> npt.NDArray[np.float64]:
        """
        Convert the PaDEL-Descriptor results to a NumPy array, excluding the
        'Name' column.

        Returns
        -------
        npt.NDArray[np.float64]
            A NumPy array containing the descriptor values, shape (n_molecules,
            n_desc_fp).
        """

        ret = (
            pd.read_csv(self._results)
            .drop(columns=["Name"])
            .to_numpy(np.float64)
        )
        self._results.seek(0)
        return ret

    def to_pandas(self) -> pandas.DataFrame:
        """
        Convert the PaDEL-Descriptor results to a Pandas DataFrame, excluding
        the 'Name' column.

        Returns
        -------
        pandas.DataFrame
            A DataFrame containing the descriptor values, shape (n_molecules,
            n_desc_fp).
        """

        ret = pd.read_csv(self._results).drop(columns=["Name"])
        self._results.seek(0)
        return ret
