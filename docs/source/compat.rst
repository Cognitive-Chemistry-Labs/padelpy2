Compatibility helpers
=====================

``padelpy2.compat`` provides additive helpers with padelpy-like names
(``from_smiles``, ``from_sdf``, ``from_mdl``). They are a **migration
convenience**, not a replacement for padelpy.

When to stay on padelpy
-----------------------

Prefer **padelpy** when you need a **stdlib-only** environment (no RDKit /
pandas) and SMILES/SDF → dict workflows over the stock JAR.

When to use ``padelpy2.compat``
--------------------------------

Use these helpers when you are moving toward RDKit + DataFrame workflows but
want familiar entry-point names. Under the hood they build RDKit molecules and
call ``Calculator`` with the **stock** Yap JAR (default: 2D descriptor catalog).

For new code, prefer constructing ``Calculator`` explicitly. For package choice
between padelpy and padelpy2, see :doc:`when_to_use`. For a padelpy → padelpy2
migration walkthrough, see :doc:`migration`.

Example
-------

::

   from padelpy2.compat import from_smiles

   df = from_smiles(["CCO", "c1ccccc1"])          # DataFrame
   row = from_smiles("CCO", as_dict=True)           # best-effort dict

``as_dict=True`` returns a ``dict`` for one molecule or a ``list`` of ``dict``
for many. Shapes may differ from padelpy’s ``OrderedDict`` output.

Import path
-----------

Import from the submodule only::

   from padelpy2.compat import from_smiles, from_sdf, from_mdl

These names are **not** re-exported on the top-level ``padelpy2`` package
(frozen public ``__all__``).
