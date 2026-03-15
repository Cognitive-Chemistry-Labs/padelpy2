![CogniChem Logo](https://cognichem.com/images/cc-logo-color.svg)
# padelpy2

[![GitHub version](https://badge.fury.io/gh/cognitive-chemistry-labs%2Fpadelpy2.svg)](https://badge.fury.io/gh/cognitive-chemistry-labs%2Fpadelpy2)
[![PyPI version](https://badge.fury.io/py/padelpy2.svg)](https://badge.fury.io/py/padelpy2)
[![GitHub license](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Cognitive-Chemistry-Labs/padelpy2/blob/main/LICENSE)

**padelpy2** is a Python wrapper for the [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) software, enabling fast and flexible calculation of molecular descriptors and fingerprints directly from Python.

---

## Features

- Compute 1D, 2D, and 3D molecular descriptors and fingerprints using PaDEL-Descriptor
- Simple, object-oriented API for descriptor/fingerprint selection and calculation
- Native support for RDKit molecules
- Highly configurable (multithreading, 3D conversion, custom descriptor sets, etc.)
- Returns results as pandas DataFrames for easy downstream analysis

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
- Python 3.7–3.11
- [RDKit](https://www.rdkit.org/) (install via conda or pip; see note above)
- pandas
- **Java Runtime Environment (JRE) 6 or higher** must be installed and available on your system PATH. PaDEL-Descriptor is a Java application and will not run without Java. You can download Java [Oracle](https://www.oracle.com/java/technologies/downloads/).

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
from padelpy2.descriptors import MolecularWeight, XLogP
calc = Calculator([MolecularWeight, XLogP])
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
- Returns: pandas DataFrame

### Descriptor and Fingerprint Sets
- `descriptors`: All available descriptors (1D, 2D, 3D)
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

For advanced use cases, you can call the low-level PaDEL-Descriptor wrapper directly. This allows you to execute the underlying Java tool with custom arguments and file-based workflows.

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

---

For more examples, see the `examples/` directory.
