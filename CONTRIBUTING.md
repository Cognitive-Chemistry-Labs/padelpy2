# Contributing to padelpy2

Thanks for your interest in contributing. This document covers local development
setup and the checks expected before opening a pull request.

## Prerequisites

- Python 3.9–3.13
- **Java Runtime Environment (JRE) 8+** on your `PATH` (`java -version`)
- For `Calculator` / most tests: pandas + RDKit (`padelpy2[calc]`; conda-forge RDKit recommended)

## Development install

```bash
git clone https://github.com/Cognitive-Chemistry-Labs/padelpy2.git
cd padelpy2
pip install -e ".[dev,docs,calc]"
```

Or conda-forge RDKit plus the pandas extra:

```bash
conda install -c conda-forge rdkit
pip install -e ".[dev,docs,pandas]"
```

## Checks

Lint and format (ruff):

```bash
ruff check padelpy2 tests
ruff format --check padelpy2 tests
```

Tests (integration tests require Java and RDKit):

```bash
pytest tests/ -q
```

Optional coverage:

```bash
pytest tests/ -q --cov=padelpy2 --cov-report=term-missing
```

Documentation:

```bash
cd docs
make html
```

HTML output is written to `docs/build/html/`.

## Pull requests

- Keep changes focused; match existing code style.
- Do not break the [frozen public API](https://cognitive-chemistry-labs.github.io/padelpy2/api_stability.html)
  without a major version discussion.
- Add or update tests when behavior changes.
- Note user-facing changes under `[Unreleased]` in `CHANGELOG.md`.
- Ensure ruff, pytest, and (when docs change) `make html` succeed locally.

## Security

Please report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the
project’s [Apache License 2.0](LICENSE).
