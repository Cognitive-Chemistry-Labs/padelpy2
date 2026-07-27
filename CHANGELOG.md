# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Stock-JAR golden oracles (`tests/fixtures/oracles_v1/`) and related regression tests
- Unit and integration tests for utils, config forwarding, catalog shapes, and mixed subsets
- Sphinx pages for installation, quickstart, when-to-use, architecture, and API stability
- `dev` and `docs` optional dependency extras; ruff and coverage configuration
- CI with Temurin 17, lint job, and Python 3.9–3.11 test matrix
- `CHANGELOG.md`, `CONTRIBUTING.md`, and `SECURITY.md`
- Optional `Calculator(..., chunk_size=N)` batching (default `None` unchanged)
- G3 timing snapshot and performance docs (`docs/design/benchmarks_g3/`, Sphinx performance page); JVM reuse deferred
- `padelpy2.compat` helpers: `from_smiles` / `from_sdf` / `from_mdl` (DataFrame default; optional `as_dict`)
- Sphinx migration guide from padelpy (`migration.rst`)
- `padelpy2.qc.summarize_descriptor_frame` / `DescriptorQCReport` (convenience QC)
- `Calculator` kwargs: `retain_names`, `on_error` (`"raise"` | `"nan"`)
- Refreshed `examples/example.ipynb` tutorial; Sphinx examples page
- `CITATION.cff` (engine preferred citation: Yap 2011)
- Coverage-gap tests (`tests/test_coverage_gaps.py`)
- Optional dependency extras: `[pandas]`, `[rdkit]`, and `[calc]` (pandas+rdkit); low-level notebook `examples/padeldescriptor_lowlevel.ipynb`
- Pytest `integration` marker for live JAR tests; faster default suite (~30s)

### Changed

- **Breaking (install):** `pandas` is no longer a hard dependency. Use `pip install "padelpy2[calc]"` for Calculator / DataFrame APIs. Default install is `padeldescriptor` + catalogs only.
- Lazy top-level `Calculator` import so `import padelpy2` does not require pandas/RDKit
- Public docs and README position padelpy vs padelpy2 only (third-party PaDEL wrapper recommendations removed; peer ePaDEL notes remain in design/parity archive)
- README positioning for stock Yap JAR vs padelpy; fixed `Weight` example
- Documentation version aligned with package metadata (`0.1.0`)
- `padeldescriptor` / `popen_timeout` use argument-list subprocess invocation (paths with spaces)
- Coverage policy: aim ≥95% locally; CI fail-under **90%** (`tool.coverage.report.fail_under`)
- Optional `[rdkit]` extra uses modern `rdkit` wheels; CI pins `rdkit==2026.3.4` on Python 3.10–3.11

### Fixed

- Public `__all__` / import hygiene and version fallback when distribution metadata is missing
