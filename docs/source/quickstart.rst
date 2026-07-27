Quickstart
==========

This page shows a minimal path from RDKit molecules to a ``pandas`` DataFrame
using the stock PaDEL JAR. Install with ``pip install "padelpy2[calc]"``.
See :doc:`installation` for Java and RDKit setup, :doc:`examples` for a
no-RDKit ``padeldescriptor`` notebook, and :doc:`when_to_use` for package choice.

Minimal example
---------------

Compute molecular weight-related descriptors for ethanol and benzene::

   from rdkit import Chem
   from rdkit.Chem import AllChem

   from padelpy2 import Calculator
   from padelpy2.descriptors import Weight

   smiles = ["CCO", "c1ccccc1"]
   mols = []
   for smi in smiles:
       mol = Chem.AddHs(Chem.MolFromSmiles(smi))
       AllChem.Compute2DCoords(mol)
       mols.append(mol)

   calc = Calculator([Weight])
   df = calc(mols)
   print(df)

By default the engine ``Name`` column is dropped from the DataFrame.

Default catalogs
----------------

Preset lists cover the stock descriptor catalogs and fingerprints::

   from padelpy2 import Calculator, descriptors_2d, descriptors_3d, fingerprints

   # Default shapes (column counts) for the stock catalogs:
   # descriptors_2d → 1444 columns
   # descriptors_3d → 431 columns  (molecules need 3D conformers)
   # descriptors    → 1875 columns
   # each fingerprint type → its n_bits columns

   df_2d = Calculator(descriptors_2d)(mols)

3D descriptors require conformers (for example ``AllChem.EmbedMolecule``).
Without them, padelpy2 fails fast with a clear error before invoking Java.

Custom subsets and fingerprints
-------------------------------

Mix descriptor classes and fingerprint types freely::

   from padelpy2.descriptors import ALOGP, Crippen, Weight
   from padelpy2.fingerprints import MACCSFingerprinter

   calc = Calculator([ALOGP, Crippen, Weight, MACCSFingerprinter])
   df = calc(mols)

Configuration
-------------

Pass a ``PaDELConfig`` to forward PaDEL CLI flags (threads, aromaticity
detection, salt removal, and others). Example::

   from padelpy2 import Calculator, PaDELConfig
   from padelpy2.descriptors import Weight

   cfg = PaDELConfig(threads=1, detectaromaticity=True)
   df = Calculator([Weight], config=cfg)(mols)

For large molecule lists, optional ``chunk_size`` processes batches and
concatenates results (default ``None`` keeps a single batch)::

   df = Calculator([Weight])(mols, chunk_size=50)

Keep the engine ``Name`` column with ``retain_names=True``. Use
``on_error="nan"`` to isolate invalid molecules or failed chunks as NaN rows
(default ``on_error="raise"`` remains fail-fast).

These options are UX parity for batching and error handling, not a claim of
unique parallel performance.

Low-level ``padeldescriptor`` (padelpy-compatible keywords) is documented in
the :doc:`api` and :doc:`architecture` pages.
