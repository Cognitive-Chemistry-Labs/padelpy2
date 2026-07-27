Installation
============

**padelpy2** drives the vendored **stock** PaDEL-Descriptor Java application.
You need a system Java runtime in addition to Python dependencies.

Requirements
------------

* Python 3.9–3.13 (see note below for the optional PyPI RDKit wheel)
* **Java Runtime Environment (JRE) 8 or higher** on your ``PATH``
  (``java -version`` should succeed). CI uses Temurin 17.
* **pandas** (installed with the package)
* **RDKit** for the ``Calculator`` API (conda recommended)

Install the package
-------------------

From PyPI::

   pip install padelpy2

From a source checkout::

   pip install -e .

RDKit
-----

Conda (recommended)::

   conda install -c conda-forge rdkit

Optional PyPI extra (current ``rdkit`` wheels; prefer 3.10+)::

   pip install "padelpy2[rdkit]"

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

   pip install -e ".[dev,docs]"

* ``[dev]`` — pytest, coverage, ruff
* ``[docs]`` — Sphinx and the Read the Docs theme

Build this documentation from a checkout::

   cd docs
   make html
