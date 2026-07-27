API stability
=============

This page records the **frozen public contract** for padelpy2 on the v0.x line
through v1.0 unless a major version bump says otherwise. Additive APIs are
welcome when they preserve the defaults below.

See also :doc:`api` (autodoc) and :doc:`architecture`.

Frozen top-level exports
------------------------

Importable from ``padelpy2`` (package ``__all__``):

* ``Calculator``
* ``PaDELConfig``
* ``__version__``
* ``descriptors``, ``descriptors_2d``, ``descriptors_3d``
* ``fingerprints``
* ``padeldescriptor``

Catalog types ``Descriptor`` and ``Fingerprint``, and individual catalog
singletons (for example ``Weight``, ``MACCSFingerprinter``), are imported from
submodules. ``padelpy2.utils`` is semi-internal (empty ``__all__``).

Frozen ``Calculator`` behavior
------------------------------

* ``Calculator(descriptors, config=None)`` — high-level calculator over the
  **stock** Yap JAR.
* ``Calculator.__call__(mols)`` returns a ``pandas.DataFrame`` and **drops** the
  engine ``Name`` column by default.
* Additive optional keyword-only arguments (defaults preserve v0.1 behavior):

  - ``chunk_size=None`` — optional batching
  - ``retain_names=False`` — drop engine ``Name`` unless ``True``
  - ``on_error="raise"`` — fail fast; ``"nan"`` isolates invalid molecules /
    failed chunks as NaN rows when a column schema is available

* Default ``PaDELConfig`` field values and ``padeldescriptor`` keyword names used
  by existing callers are stable.

Default catalog column counts
-----------------------------

These shapes are guarded in CI (metadata counts and live ``Calculator`` runs):

.. list-table::
   :header-rows: 1
   :widths: 40 20

   * - Catalog
     - Columns
   * - ``descriptors_2d``
     - 1444
   * - ``descriptors_3d``
     - 431
   * - ``descriptors``
     - 1875
   * - Each fingerprint
     - ``Fingerprint.n_bits``

Stock-JAR golden oracles under ``tests/fixtures/oracles_v1/`` pin representative
values for these catalogs.

Excluded from default lists
---------------------------

The following descriptors exist as importable singletons but are **not** in the
default ``descriptors`` / ``descriptors_2d`` lists:

* ``AminoAcidCount``
* ``IPMolecularLearning``
* ``KierHallSmarts``

Stability checklist (do not break without a major version)
----------------------------------------------------------

* Signatures of ``Calculator.__init__`` and ``Calculator.__call__`` (required
  arguments)
* Default contents of ``descriptors`` / ``descriptors_2d`` / ``descriptors_3d`` /
  ``fingerprints``
* Default dropping of the ``Name`` column
* ``padeldescriptor`` keyword names used by existing callers
* Default ``PaDELConfig`` field values
