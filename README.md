![CogniChem Logo](https://cognichem.com/images/cc-logo-color.svg)
# padelpy2

[![GitHub version](https://badge.fury.io/gh/cognitive-chemistry-labs%2Fpadelpy2.svg)](https://badge.fury.io/gh/cognitive-chemistry-labs%2Fpadelpy2)
[![PyPI version](https://badge.fury.io/py/padelpy2.svg)](https://badge.fury.io/py/padelpy2)
[![GitHub license](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Cognitive-Chemistry-Labs/padelpy2/blob/main/LICENSE)

**padelpy2** is a Python bridge to the **stock** [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) Java application (Yap, 2011). It provides an RDKit-native `Calculator` with `pandas` DataFrame results, typed descriptor/fingerprint catalogs, and a low-level `padeldescriptor` CLI surface compatible with [padelpy](https://github.com/ecrl/padelpy).

**Documentation:** [API and guides](https://cognitive-chemistry-labs.github.io/padelpy2/) · [When to use which package](https://cognitive-chemistry-labs.github.io/padelpy2/when_to_use.html)

## When to use

| Need | Prefer |
|------|--------|
| Minimal env; SMILES/SDF → dicts; no RDKit/pandas | [padelpy](https://github.com/ecrl/padelpy) |
| Stock Yap JAR, `padeldescriptor` continuity, RDKit → DataFrame | **padelpy2** (this package) |
| General descriptors without PaDEL identity | mordredcommunity or RDKit |

See the [when-to-use guide](https://cognitive-chemistry-labs.github.io/padelpy2/when_to_use.html) for stock-JAR fidelity notes.

## Features

- Stock Yap PaDEL-Descriptor JAR (same family as padelpy)
- RDKit `Mol` → `pandas` DataFrame via `Calculator`
- Typed 2D/3D descriptor and fingerprint catalogs; custom subsets
- `PaDELConfig` for PaDEL CLI-aligned options (threads, aromaticity, salts, …)
- Low-level `padeldescriptor` for file-based / padelpy-style workflows
- Regression oracles pinning stock-JAR column schemas and values

---

## Installation

### From PyPI

```bash
pip install padelpy2
```

### With RDKit (PyPI version)

If you do not already have RDKit installed, you can install the PyPI build (version 2022.9.5) with:

```bash
pip install padelpy2[rdkit]
```

> **Note:** The PyPI build of RDKit (`rdkit-pypi==2022.9.5`) is limited and may not support all features or platforms. For best compatibility and performance, it is **strongly recommended** to install RDKit via [conda](https://www.rdkit.org/docs/Install.html) or your preferred package manager.

### From Source

```bash
git clone https://github.com/cognitive-chemistry-labs/padelpy2
cd padelpy2
pip install .
```

**Requirements:**
- Python 3.9–3.13  
	<sup>\*If installing RDKit from pip, only Python 3.9–3.11 are supported. For Python 3.12+ use conda or another supported method.</sup>
- [RDKit](https://www.rdkit.org/) (install via conda or pip; see note above)
- pandas
- **Java Runtime Environment (JRE) 8 or higher** must be installed and available on your system PATH. PaDEL-Descriptor is a Java application and will not run without Java. padelpy2 does not auto-download a JRE.

---

## Quick Start

```python
from rdkit import Chem
from padelpy2 import Calculator, descriptors

# Example molecules (SMILES)
smiles = [
    "CN=C=O",
    "CC(=O)NCCC1=CNc2c1cc(OC)cc2",
    "OCCc1c(C)[n+](cs1)Cc2cnc(C)nc2N",
]
mols = [Chem.AddHs(Chem.MolFromSmiles(smi)) for smi in smiles]

# Calculate all available descriptors
calc = Calculator(descriptors)
results = calc(mols)
print(results)
```

---

## Usage Examples

### Calculate 2D Descriptors Only
```python
from padelpy2 import Calculator, descriptors_2d
calc = Calculator(descriptors_2d)
results = calc(mols)
```

### Calculate 3D Descriptors Only
```python
from padelpy2 import Calculator, descriptors_3d
calc = Calculator(descriptors_3d)
results = calc(mols)
```

### Calculate Fingerprints
```python
from padelpy2 import Calculator, fingerprints
calc = Calculator(fingerprints)
results = calc(mols)
```

### Calculate Specific Descriptors
```python
from padelpy2.descriptors import Weight, XLogP
calc = Calculator([Weight, XLogP])
results = calc(mols)
```

### Calculate a Specific Fingerprint
```python
from padelpy2.fingerprints import MACCSFingerprinter
calc = Calculator([MACCSFingerprinter])
results = calc(mols)
```

---

## API Overview

### Calculator
The main interface for descriptor/fingerprint calculation.

```python
Calculator(descriptors: Iterable[Descriptor or Fingerprint], config: PaDELConfig = None)
```
- `descriptors`: List of descriptor/fingerprint objects (see below)
- `config`: Optional configuration (threads, 3D conversion, etc.)

#### Call
```python
results = calc(mols)
```
- `mols`: List of RDKit Mol objects
- Returns: pandas DataFrame (engine `Name` column dropped by default)

### Descriptor and Fingerprint Sets
- `descriptors`: All available descriptors (2D and 3D)
- `descriptors_2d`: Only 2D descriptors
- `descriptors_3d`: Only 3D descriptors
- `fingerprints`: All available fingerprints

### Custom Configuration
```python
from padelpy2 import PaDELConfig
config = PaDELConfig(threads=4, convert3d=True)
calc = Calculator(descriptors, config=config)
```

---

## Low-Level Wrapper Usage

For advanced use cases, you can call the low-level PaDEL-Descriptor wrapper directly. This allows you to execute the underlying Java tool with custom arguments and file-based workflows. The keyword surface is aligned with padelpy for migration continuity.

### Example: Using the `padeldescriptor` Function

```python
from padelpy2.wrapper import padeldescriptor

# Calculate 2D descriptors for a directory of structure files (e.g., SDF or MOL)
output_csv = padeldescriptor(
    d_2d=True,
    mol_dir="/path/to/structures/",  # directory or file with molecules
    d_file="/path/to/output.csv",    # output CSV file
    threads=4,                       # number of threads
    headless=True                    # run in headless mode (no GUI)
)
print(f"Results written to: {output_csv}")
```

#### Key Parameters
- `mol_dir`: Path to a directory or file containing molecular structures (SDF, MOL, etc.)
- `d_file`: Output file for descriptors (CSV)
- `d_2d`, `d_3d`, `fingerprints`: Enable calculation of 2D, 3D descriptors, or fingerprints
- `threads`: Number of threads to use
- `config`, `descriptortypes`: Optional config or descriptor type files
- `convert3d`, `removesalt`, `retainorder`, etc.: Advanced options (see docstring in `padelpy2/wrapper.py`)
- `use_tempfile`: If `True` and `d_file` is not set, a temporary file is used for output

Returns the path to the output file, or raises an error if the calculation fails.

See the function docstring in `padelpy2/wrapper.py` for a full list of options and details.

---

## Links

- [PaDEL-Descriptor Homepage](http://www.yapcwsoft.com/dd/padeldescriptor/)
- [Project Repository](https://github.com/cognitive-chemistry-labs/padelpy2)
- [Documentation](https://cognitive-chemistry-labs.github.io/padelpy2/)
- [When to use](https://cognitive-chemistry-labs.github.io/padelpy2/when_to_use.html)
- [Migrating from padelpy](https://cognitive-chemistry-labs.github.io/padelpy2/migration.html)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

---

## Examples

- Tutorial notebook: [`examples/example.ipynb`](examples/example.ipynb) (install notes, MWE, aromatic config, custom subset)
- Docs: [Examples](https://cognitive-chemistry-labs.github.io/padelpy2/examples.html)
