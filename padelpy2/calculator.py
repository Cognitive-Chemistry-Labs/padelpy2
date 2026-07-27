from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Literal

import numpy as np

from padelpy2._extras import require_pandas, require_rdkit
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Descriptor
from padelpy2.fingerprints import Fingerprint
from padelpy2.utils import (
    check_for_invalid_mols,
    count_descriptor_types,
    create_descriptortypes_xml,
    remove_files,
    write_mols_to_tempfile,
    write_xml_string_to_tempfile,
)
from padelpy2.wrapper import padeldescriptor

if TYPE_CHECKING:
    import pandas as pd
    from rdkit.Chem import Mol

# Fail fast with an actionable message when optional deps are missing.
pd = require_pandas()
require_rdkit()

__all__ = ["Calculator"]


class Calculator:
    """
    A class to compute chemical descriptors and fingerprints using
    PaDEL-Descriptor.

    Parameters
    ----------
    descriptors : Iterable[Descriptor or Fingerprint]
        An iterable of Descriptor or Fingerprint objects.
    config : padelpy2.config.PaDELConfig or None, optional
        Configuration for PaDEL. If None, a default configuration is used
        (default=None).

    Attributes
    ----------
    config : padelpy2.config.PaDELConfig
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
        descriptors: Iterable[Descriptor | Fingerprint],
        config: PaDELConfig | None = None,
    ):

        if config is None:
            config = PaDELConfig()
        self.config = config
        self._items = list(descriptors)

        self.xml = create_descriptortypes_xml(self._items)
        self.n_2d, self.n_3d, self.n_fp = count_descriptor_types(self._items)

    def __call__(
        self,
        mols: list[Mol],
        *,
        chunk_size: int | None = None,
        retain_names: bool = False,
        on_error: Literal["raise", "nan"] = "raise",
    ) -> pd.DataFrame:
        """
        Calculates descriptors and/or fingerprints for a list of RDKit Mol
        objects.

        Parameters
        ----------
        mols : list of Mol
            A list of RDKit Mol objects.
        chunk_size : int or None, optional
            If set to a positive integer, molecules are processed in successive
            batches of at most ``chunk_size`` and the resulting DataFrames are
            concatenated in order. ``None`` (default) runs a single batch.
        retain_names : bool, default False
            If True, keep the engine ``Name`` column; if False (default), drop it.
        on_error : {"raise", "nan"}, default "raise"
            ``raise`` fails fast (v0.1 behavior). ``nan`` isolates invalid
            molecules and failed chunks as all-NaN rows when a column schema is
            available.

        Returns
        -------
        pd.DataFrame
            A DataFrame containing the computed descriptors and/or
            fingerprints.
        """

        if chunk_size is not None and chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer or None.")
        if on_error not in ("raise", "nan"):
            raise ValueError("on_error must be 'raise' or 'nan'.")

        check_3d = self.n_3d > 0
        if on_error == "raise":
            check_for_invalid_mols(mols, check_3d)
            valid_indices = list(range(len(mols)))
        else:
            valid_indices = []
            for i, mol in enumerate(mols):
                try:
                    check_for_invalid_mols([mol], check_3d)
                except ValueError:
                    continue
                valid_indices.append(i)

        valid_mols = [mols[i] for i in valid_indices]
        xml_file_name = write_xml_string_to_tempfile(self.xml)
        try:
            if not valid_mols:
                columns = self._columns_from_catalog()
                if columns is None:
                    raise ValueError(
                        "on_error='nan' could not infer columns for an empty "
                        "valid set when fingerprints are included; provide at "
                        "least one valid molecule."
                    )
                result = self._nan_frame(len(mols), columns, retain_names)
                if retain_names:
                    result["Name"] = [f"mol_{i}" for i in range(len(mols))]
                return result

            if chunk_size is None:
                try:
                    computed = self._run_batch(
                        valid_mols, xml_file_name, retain_names=retain_names
                    )
                except (RuntimeError, TimeoutError, OSError):
                    if on_error == "raise":
                        raise
                    columns = self._columns_from_catalog()
                    if columns is None:
                        raise
                    computed = self._nan_frame(len(valid_mols), columns, retain_names)
            else:
                computed = self._run_chunked(
                    valid_mols,
                    xml_file_name,
                    chunk_size=chunk_size,
                    retain_names=retain_names,
                    on_error=on_error,
                )

            return self._align_rows(
                computed,
                n_total=len(mols),
                valid_indices=valid_indices,
                retain_names=retain_names,
            )
        finally:
            remove_files(xml_file_name)

    def _columns_from_catalog(self) -> list[str] | None:
        columns: list[str] = []
        for item in self._items:
            if type(item) is Fingerprint:
                return None
            if type(item) is Descriptor:
                columns.extend(item.descriptors)
        return columns

    def _nan_frame(
        self, n_rows: int, columns: list[str], retain_names: bool
    ) -> pd.DataFrame:
        cols = list(columns)
        if retain_names and "Name" not in cols:
            cols = ["Name", *cols]
        data = {
            c: (
                [f"mol_{i}" for i in range(n_rows)]
                if c == "Name"
                else np.full(n_rows, np.nan, dtype=float)
            )
            for c in cols
        }
        return pd.DataFrame(data)

    def _align_rows(
        self,
        computed: pd.DataFrame,
        *,
        n_total: int,
        valid_indices: list[int],
        retain_names: bool,
    ) -> pd.DataFrame:
        if len(valid_indices) == n_total:
            return computed.reset_index(drop=True)

        columns = list(computed.columns)
        value_cols = [c for c in columns if c != "Name"]
        out = self._nan_frame(n_total, value_cols, retain_names=retain_names)
        computed = computed.reset_index(drop=True)
        for row_pos, mol_index in enumerate(valid_indices):
            for col in value_cols:
                out.at[mol_index, col] = computed.at[row_pos, col]
            if retain_names and "Name" in computed.columns:
                out.at[mol_index, "Name"] = computed.at[row_pos, "Name"]
            elif retain_names:
                out.at[mol_index, "Name"] = f"mol_{mol_index}"
        return out

    def _run_chunked(
        self,
        mols: list[Mol],
        xml_file_name: str,
        *,
        chunk_size: int,
        retain_names: bool,
        on_error: Literal["raise", "nan"],
    ) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        schema: list[str] | None = None
        for start in range(0, len(mols), chunk_size):
            chunk = mols[start : start + chunk_size]
            try:
                part = self._run_batch(chunk, xml_file_name, retain_names=retain_names)
                schema = list(part.columns)
                frames.append(part)
            except (RuntimeError, TimeoutError, OSError):
                if on_error == "raise":
                    raise
                if schema is None:
                    schema = self._columns_from_catalog()
                    if schema is None:
                        raise
                    if retain_names and "Name" not in schema:
                        schema = ["Name", *schema]
                frames.append(
                    self._nan_frame(len(chunk), schema, retain_names=retain_names)
                )
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def _run_batch(
        self,
        mols: list[Mol],
        xml_file_name: str,
        *,
        retain_names: bool,
    ) -> pd.DataFrame:
        sd_file_name = write_mols_to_tempfile(mols)
        try:
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
                use_tempfile=True,
            )
            df = pd.read_csv(results_file_name)
            if not retain_names:
                df = df.drop(columns=["Name"])
            remove_files(results_file_name)
            return df
        finally:
            remove_files(sd_file_name)
