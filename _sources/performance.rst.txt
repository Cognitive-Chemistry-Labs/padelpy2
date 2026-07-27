Performance notes
=================

padelpy2 starts the **stock** PaDEL-Descriptor CLI (``java -jar``) for each
``padeldescriptor`` call. Timing numbers below are a **local snapshot**, not a
claim of unique speed versus other descriptor engines.

JVM reuse (deferred)
--------------------

True JVM keep-alive / warm workers are **not implemented**. The vendored stock
JAR exposes no keep-alive worker API. Reuse would require a custom long-lived
process protocol, which is out of scope for G3. For large molecule lists, use
optional ``chunk_size`` on ``Calculator.__call__`` (see :doc:`quickstart`).
Each chunk still starts a new JVM, so chunking bounds batch size and may
**increase** wall time for small descriptor sets.

Measured snapshot
-----------------

Regenerated with::

   python scripts/bench_padelpy2.py --sizes 10,100

Full method notes and machine-readable JSON live in the repository under
``docs/design/benchmarks_g3/`` (see ``METHOD.md`` and ``RESULTS.md``).

**Hardware / environment (snapshot):** macOS arm64; Python 3.11.8; RDKit
2026.03.4; padelpy2 0.2.0; stock JAR sha256
``f13940cd98dcdeadc54124f4111081c740fcc6effbfa33cf494125b707cad133``;
``PaDELConfig(threads=1)``; ethanol × N; descriptor ``Weight``; chunk size 25.

.. list-table:: Wall seconds (illustrative)
   :header-rows: 1
   :widths: 20 10 15 15 20

   * - Engine
     - N
     - chunk_size
     - cold_s
     - second_call_s
   * - padelpy2
     - 10
     - —
     - 0.89
     - 0.71
   * - padelpy2
     - 10
     - 25
     - 0.70
     - 0.71
   * - padelpy2
     - 100
     - —
     - 0.81
     - 0.82
   * - padelpy2
     - 100
     - 25
     - 2.90
     - 2.92

``second_call_s`` is a second ``java -jar`` process (OS cache warm), not an
in-process JVM.

Interpretation
--------------

* Cold startup of the stock JAR dominates for small N and small catalogs.
* Chunking with the stock CLI is **not** a free speedup: more chunks means more
  JVM starts. Prefer single-batch runs unless you need smaller per-batch
  footprints.
* Prefer single-batch ``Calculator`` calls unless you need smaller per-batch
  footprints; see :doc:`when_to_use` for package choice.

See also :doc:`architecture` and :doc:`api_stability`.
