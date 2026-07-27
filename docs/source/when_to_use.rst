When to use which package
=========================

Users who need **PaDEL-family** features in Python typically choose between
**padelpy** (thin stdlib CLI) and **padelpy2** (RDKit → DataFrame over the same
stock JAR). padelpy2 is **not** a general replacement for Mordred, RDKit
descriptors, or other non-PaDEL engines.

Decision table
--------------

.. list-table::
   :header-rows: 1
   :widths: 70 30

   * - Need
     - Prefer
   * - Minimal environment; SMILES/SDF → dicts; no RDKit or pandas
     - **padelpy**
   * - Stock Yap JAR; padelpy-compatible ``padeldescriptor``; RDKit → DataFrame;
       oracle-tested columns
     - **padelpy2**
   * - General descriptors without PaDEL identity
     - **mordredcommunity** / RDKit

Links: `padelpy <https://github.com/ecrl/padelpy>`_,
`mordredcommunity <https://github.com/JacksonBurns/mordred-community>`_,
`RDKit <https://www.rdkit.org/>`_.

Stock JAR fidelity
------------------

padelpy2 vendors the **classic Yap stock JAR** (same family as padelpy). Column
schemas and numeric values are pinned by regression oracles in the repository.
Defaults such as ``detectaromaticity=False`` are part of that fidelity contract
(aromatic counts on benzene often stay at zero unless you opt in). Treat
outputs from other PaDEL-family distributions as a different engine unless you
have verified them yourself.

Why not merge into padelpy?
---------------------------

RDKit and pandas would break padelpy’s stdlib-only identity. padelpy remains the
right choice for a minimal CLI/dict workflow over the stock JAR.

Who should use what
-------------------

* **QSAR / classic PaDEL columns** — prefer padelpy2 (or padelpy) when models
  were trained on stock-JAR outputs.
* **padelpy migrators** — padelpy2 for RDKit + DataFrame while keeping stock-JAR
  semantics and familiar CLI keywords.
* **General cheminformatics descriptors** — Mordred or RDKit when PaDEL column
  identity is not required.

Migration helpers with padelpy-like names live in :doc:`compat` (RDKit required;
not a stdlib-only substitute for padelpy).

See also :doc:`architecture` and :doc:`api`.
