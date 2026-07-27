Descriptor QC helpers
=====================

``padelpy2.qc`` provides a small convenience summary for descriptor/fingerprint
DataFrames. This is convenience UX only—not a substitute for Mordred, RDKit, or
dedicated data-quality libraries.

Usage
-----

::

   from padelpy2 import Calculator, descriptors_2d
   from padelpy2.qc import summarize_descriptor_frame

   df = Calculator(descriptors_2d)(mols)
   report = summarize_descriptor_frame(df)
   print(report.n_rows, report.n_cols)
   print(report.constant_columns[:10])
   print(report.non_finite_columns)

``DescriptorQCReport`` fields
-----------------------------

* ``n_rows`` / ``n_cols`` — frame shape
* ``nan_fraction`` — per-column fraction of NaN (after numeric coercion)
* ``constant_columns`` — columns with one distinct non-NaN value, or all-NaN
* ``non_finite_columns`` — columns containing ``±inf``

Import from the submodule only::

   from padelpy2.qc import DescriptorQCReport, summarize_descriptor_frame

These names are not part of the frozen top-level ``padelpy2.__all__``.
