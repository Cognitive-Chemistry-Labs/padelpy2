Installation
============

**padelpy2** drives the vendored **stock** PaDEL-Descriptor Java application.
You need a system Java runtime in addition to Python dependencies.

Requirements
------------

* Python 3.9–3.13 (RDKit wheels for oracle-tested versions prefer 3.10+)
* **Java Runtime Environment (JRE) 8 or higher** on your ``PATH``
  (``java -version`` should succeed). CI uses Temurin 17.

Optional extras
---------------

* **None (default)** — low-level ``padeldescriptor`` CLI wrapper (stdlib + Java)
* ``[pandas]`` — DataFrame helpers (``qc``; used by Calculator)
* ``[rdkit]`` — RDKit molecule I/O for Calculator / ``compat``
* ``[calc]`` — ``pandas`` + ``rdkit`` (recommended for ``Calculator``)

Install the package
-------------------

Minimal (``padeldescriptor`` only)::

   pip install padelpy2

Calculator / DataFrame workflows::

   pip install "padelpy2[calc]"

From a source checkout::

   pip install -e ".[calc]"

RDKit
-----

Conda (recommended) plus the pandas extra::

   conda install -c conda-forge rdkit
   pip install "padelpy2[pandas]"

Or the combined PyPI extra (current ``rdkit`` wheels; prefer 3.10+)::

   pip install "padelpy2[calc]"

Stock-JAR oracle fixtures were generated with RDKit 2026.03.x. Prefer
conda-forge RDKit when possible.

Java notes
----------

PaDEL-Descriptor will not run without ``java`` on ``PATH``. padelpy2 does
**not** bundle or auto-download a JRE; install a system JRE (8+) and ensure
``java`` is on ``PATH``. See :doc:`when_to_use` for package choice.

Development extras
------------------

::

   pip install -e ".[dev,docs,calc]"

* ``[dev]`` — pytest, coverage, ruff
* ``[docs]`` — Sphinx and the Read the Docs theme
* ``[calc]`` — pandas + RDKit for API autodoc and examples

Build this documentation from a checkout::

   cd docs
   make html
