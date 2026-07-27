Migrating from padelpy
======================

This guide helps users of `padelpy <https://github.com/ecrl/padelpy>`_
(baseline **≥ 0.1.17**) move selected workflows to **padelpy2** while keeping
the **stock Yap PaDEL-Descriptor JAR**.

padelpy2 does **not** replace padelpy. For choosing between them, start with
:doc:`when_to_use`.

Should you migrate?
-------------------

**Stay on padelpy** if you need a **stdlib-only** stack (no RDKit, no pandas)
and SMILES/SDF → dict helpers.

**Migrate toward padelpy2** if you want RDKit molecules, ``pandas`` DataFrames,
typed catalogs, and stock-JAR continuity (including ``padeldescriptor``).

Stock JAR continuity
--------------------

padelpy and padelpy2 both drive the **classic stock JAR** family. Migration here
preserves that identity. Do not assume numeric agreement with other
PaDEL-family distributions without your own checks.

Concept mapping
---------------

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - padelpy
     - padelpy2
     - Notes
   * - ``from_smiles`` / ``from_sdf`` / ``from_mdl``
     - ``padelpy2.compat.from_smiles`` (etc.)
     - DataFrame by default; RDKit required
   * - Return ``OrderedDict`` / list of dicts
     - DataFrame, or ``as_dict=True``
     - ``as_dict`` is best-effort, not identical
   * - ``padeldescriptor(...)``
     - ``padelpy2.padeldescriptor(...)`` or
       ``from padelpy2.wrapper import padeldescriptor``
     - Same keyword-oriented CLI surface
   * - (no Calculator)
     - ``Calculator(catalog, config=...)``
     - Preferred for new RDKit-native code
   * - Default descriptor run (``-2d``)
     - compat default: ``descriptors_2d``
     - 3D catalogs need conformers via ``Calculator``

Side-by-side examples
---------------------

padelpy (dict-oriented)::

   from padelpy import from_smiles

   row = from_smiles("CCO")  # OrderedDict-like mapping

padelpy2 compat (DataFrame-oriented)::

   from padelpy2.compat import from_smiles

   df = from_smiles("CCO")                 # one-row DataFrame
   row = from_smiles("CCO", as_dict=True)  # best-effort dict

RDKit-native Calculator (recommended for new code)::

   from rdkit import Chem
   from rdkit.Chem import AllChem
   from padelpy2 import Calculator
   from padelpy2.descriptors import Weight

   mol = Chem.AddHs(Chem.MolFromSmiles("CCO"))
   AllChem.Compute2DCoords(mol)
   df = Calculator([Weight])([mol])

Low-level CLI (both packages)::

   # padelpy
   from padelpy import padeldescriptor

   # padelpy2 — keyword surface aligned for continuity
   from padelpy2 import padeldescriptor

Behavioral differences
----------------------

* **Dependencies:** padelpy2 ``compat`` and ``Calculator`` require RDKit and
  pandas; padelpy does not.
* **Return type:** DataFrames drop the engine ``Name`` column by default.
* **``as_dict``:** Convenient for migration scripts; do not assume identical
  key sets or ``OrderedDict`` ordering versus padelpy.
* **Fingerprints / descriptors flags:** compat ``descriptors=True`` selects the
  default **2D** catalog; ``fingerprints=True`` adds all fingerprint types.
* **Java:** Both expect a system JRE on ``PATH``. Neither auto-downloads a JRE.

Validation checkpoint
---------------------

1. Install padelpy2 with RDKit (see :doc:`installation`) in an environment that
   can also import padelpy if you want a side-by-side check.
2. Run a single ethanol SMILES through ``padelpy2.compat.from_smiles`` and
   confirm a DataFrame with the expected column count for your flags (default
   2D catalog → 1444 columns; see :doc:`api_stability`).
3. For numeric continuity on a small subset, compare ``Weight`` (or ALOGP /
   Crippen / Weight) via ``Calculator`` against your historical stock-JAR CSV.
   Use stock-JAR (or padelpy2 oracle) values as the reference—not another
   PaDEL-family distribution.
4. Keep using padelpy unchanged for any stdlib-only deployment paths.

See also
--------

* :doc:`when_to_use` — package choice
* :doc:`compat` — helper reference
* :doc:`quickstart` — Calculator workflow
* :doc:`performance` — chunking and JVM notes
