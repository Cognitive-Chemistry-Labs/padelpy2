Architecture
============

This page documents the package architectural philosophy and the enforceable
design rules that keep the codebase coherent. Stable policy identifiers
(``ARCH-NNN``) keep this narrative aligned with the maintainer-local
verification policy. The full design rationale lives in
``docs/design/DESIGN.md`` (approved v0.3).

Purpose
-------

**padelpy2** owns a Python bridge to the **stock** PaDEL-Descriptor Java JAR:
typed descriptor/fingerprint catalogs, an RDKit-native ``Calculator``,
``pandas`` DataFrame results, and a low-level ``padeldescriptor`` CLI surface
compatible with padelpy. Primary users need classic-JAR fidelity (including
aromatic-molecule defaults pinned by oracles) and padelpy continuity.

Non-goals include reimplementing PaDEL in pure Python, competing with Mordred
or RDKit as a general descriptor engine, and multi-engine backends behind
``Calculator``.

Principles
----------

* ``ARCH-010`` — Layered architecture with acyclic imports (higher layers
  depend only on lower layers).
* ``ARCH-020`` — Public subpackages expose a curated ``__all__``.
* ``ARCH-030`` — The Java engine is reached only through the engine-adapter
  layer (``padelpy2.wrapper`` / internal worker); orchestration must not spawn
  ad hoc ``java`` processes elsewhere.
* ``ARCH-040`` — Default public API behavior is stable: preset catalog column
  schemas and dropping the ``Name`` column unless an additive opt-in says
  otherwise. See :doc:`api_stability`.
* ``ARCH-050`` — Optional heavy dependencies (RDKit) stay behind clear import
  boundaries and documented extras.
* ``ARCH-055`` — Vendored engine is the **stock Yap JAR**; document identity
  (path/hash) wherever fidelity is claimed.
* ``ARCH-060`` — This page remains the public architecture contract.

Architecture style
------------------

**Layered package** with a functional core (catalog metadata, XML/SDF
preparation, validation) and an imperative shell (subprocess or long-lived
JVM worker).

Component map
-------------

======= =========================================== ============================
Layer   Components                                  Responsibility
======= =========================================== ============================
L0      ``padelpy2/PaDEL-Descriptor/``              Stock JAR, CSVs, notices
L1      ``descriptors``, ``fingerprints``,          Catalogs, config, I/O utils
        ``config``, ``utils``
L2      ``wrapper``                                 Java CLI / worker adapter
L3      ``calculator``                              End-to-end orchestration
L4      ``compat``, ``qc`` (shipped)                Migration helpers, QC reports
======= =========================================== ============================

Dependency rules
----------------

* L4 → L3 → L2 → L1 → L0 only (no upward or cyclic imports).
* ``compat`` and ``qc`` may use ``Calculator`` and catalog types; they must not
  bypass the wrapper to invoke Java.
* Vendored assets under ``PaDEL-Descriptor/`` are opaque binary/metadata inputs,
  not a Python import graph.

Public API
----------

Top-level exports (see package ``__init__``): ``Calculator``, ``PaDELConfig``,
``descriptors``, ``descriptors_2d``, ``descriptors_3d``, ``fingerprints``,
``padeldescriptor``, and ``__version__``.

Submodule catalogs: ``padelpy2.descriptors`` and ``padelpy2.fingerprints``
expose ``Descriptor`` / ``Fingerprint`` types and named singletons.

``ARCH-020`` requires each listed public package to declare an explicit
``__all__`` as packaging matures.

Domain types
------------

* ``Descriptor`` — PaDEL descriptor class name, member names/descriptions,
  2D/3D flag.
* ``Fingerprint`` — PaDEL fingerprint class name, bit count, description.
* ``PaDELConfig`` — dataclass of engine flags and subprocess timeout.
* Calculation results — ``pandas.DataFrame`` rows aligned with input molecule
  order when ``retainorder`` is enabled (default).

Extension points
----------------

* Pass custom iterables of ``Descriptor`` / ``Fingerprint`` instances into
  ``Calculator``.
* Low-level ``padeldescriptor`` for file/directory workflows (padelpy continuity).
* Additive ``padelpy2.compat`` provides padelpy-like ``from_smiles`` /
  ``from_sdf`` / ``from_mdl`` helpers (not a padelpy replacement).
  ``padelpy2.qc`` summarizes DataFrame missingness/constants (convenience only).
  Do not introduce alternate descriptor engines as drop-in ``Calculator``
  backends without a design revision.

Data and control flow
---------------------

1. Construct ``Calculator`` with catalog objects → build descriptortypes XML.
2. On call: validate RDKit molecules → write temporary SDF → invoke stock-JAR
   adapter → read CSV → return DataFrame (``Name`` dropped by default).
3. Optional ``chunk_size`` batches molecules behind the same public call
   signature (UX parity). JVM keep-alive is **deferred**: each stock-JAR call
   starts ``java -jar``; see :doc:`performance`.

Exceptions
----------

* Temporary flat package layout (not ``src/``) is accepted until packaging
  friction warrants migration (``ARCH-X001``).
* Shape-only integration tests are a known validation gap until stock-JAR
  fidelity oracles land (``ARCH-X002``); see design goals G2.

Change process
--------------

Update this page and the maintainer-local architecture policy together when
rules change. Keep policy identifiers stable; prefer adding a new identifier
over silently redefining an existing one. Align narrative changes with
``docs/design/DESIGN.md``.
