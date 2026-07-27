# Pre-release readiness — padelpy2 0.2.0

**Date:** 2026-07-27  
**Tier:** minor (post Phase 0–4 modernization), not JOSS  
**Verdict:** READY (with warnings)

## Version bump plan (agreed)

| Item | Decision |
|------|----------|
| Next tag | **0.2.0** |
| Rationale | Design roadmap 0.2–0.4 work is complete (oracles, Sphinx, G3 chunking, compat/QC, Calculator kwargs, tutorial). Fold into one minor. |
| `pyproject.toml` / `CITATION.cff` today | Remain **0.1.0** until `python-package-release` |
| CHANGELOG | Keep entries under `[Unreleased]`; move to `## [0.2.0] - YYYY-MM-DD` at release time |

## JOSS

**Defer.** Statement of need (classic Yap JAR fidelity + padelpy continuity + oracles) still holds after G0 PARTIAL. Missing for JOSS tier: `paper.md` / `paper.bib`, CoC, draft-PDF CI, impact ledger, Zenodo plan. Revisit after 0.2.0 if desired.

## Coverage

| Policy | Value | Status |
|--------|-------|--------|
| Aim | ≥95% line (excl. vendored JAR) | **Met** — **98.5%** local |
| CI fail-under | **90%** | Enforced via `tool.coverage.report.fail_under = 90` in `pyproject.toml` |

## Checklist

### Metadata

- [x] Version source: `pyproject.toml` `0.1.0` (bump at release)
- [x] `CITATION.cff` added (version synced to 0.1.0 until release)
- [x] `CHANGELOG.md` has `[Unreleased]` entries for this train
- [x] LICENSE / README present; `requires-python = ">=3.9,<3.14"`
- [ ] Classifiers sparse (warning only)

### Quality

- [x] `ruff check` + `ruff format --check` pass
- [x] Full `pytest` pass locally (74 tests)
- [x] Coverage ≥90% fail-under; aim ≥95% met
- [x] Added `tests/test_coverage_gaps.py` for Calculator/compat/wrapper/init gaps

### Documentation

- [x] `sphinx-build -W -b html` succeeds (fixed compat underline + PaDELConfig autodoc ambiguity)
- [x] Public docs free of `.dev` / blueprint / agent-tooling refs
- [x] Tutorial notebook path documented (`examples` + Sphinx)

### Packaging

- [x] `python -m build` succeeds (`padelpy2-0.1.0` sdist + wheel)
- [x] Clean venv: wheel + RDKit extras → `import padelpy2` OK
- [x] No agent tooling in wheel
- [ ] Wheel/sdist currently include `tests/` (flat layout; warning)
- [ ] Importing padelpy2 requires RDKit at runtime even though RDKit is an optional extra (pre-existing; warning)

### CI / release infra

- [x] Workflows: `run_tests.yml` (lint + Java + coverage), `docs.yml`, `publish_to_pypi.yml`
- [ ] Latest GitHub Actions green runs are scheduled (May 2026); **current tree not yet CI-verified on remote** — push/PR will confirm
- [ ] PyPI trusted publisher: maintainer confirms at release time

### Governance

- [x] `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `CITATION.cff`
- [ ] Issue/PR templates optional until 1.0
- [ ] `CODE_OF_CONDUCT.md` optional until 1.0 / JOSS

## Blockers

None for cutting **0.2.0** after a green CI run on the release branch/PR.

## Warnings

1. Run CI on a PR/push before tagging (local green ≠ remote green yet).
2. RDKit is imported at package import time but listed as an optional extra.
3. Packaging includes `tests/` in sdist/wheel (harmless but noisy).
4. PyPI classifiers minimal; expand if desired at release.
5. JOSS deferred (see above).

## Verified commands

```bash
ruff check padelpy2 tests && ruff format --check padelpy2 tests
pytest tests/ --cov=padelpy2 --cov-report=term-missing
cd docs && sphinx-build -W -b html source build/html
python -m build
# clean venv:
python -m venv /tmp/padelpy2-prerelease
/tmp/padelpy2-prerelease/bin/pip install dist/padelpy2-*.whl 'rdkit-pypi==2022.9.5' 'numpy==1.26.4'
/tmp/padelpy2-prerelease/bin/python -c "import padelpy2; print(padelpy2.__version__)"
```

## Recommended next step

Run **`python-package-release`** for **0.2.0** when ready (version bump, CHANGELOG section, tag, GitHub Release, PyPI). Confirm CI green on that commit first.
