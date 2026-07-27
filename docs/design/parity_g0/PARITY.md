# G0 engine parity report

**Date (UTC):** 2026-07-27T02:35:12.311406+00:00

Historical comparison of padelpy2’s **stock Yap JAR** against a peer **ePaDEL**
bundle on a fixed SMILES set. The peer package name is omitted from public and
maintainer docs by design; this archive records scientific outcome only.

## Environment

- padelpy2 `0.1.0` (stock JAR sha256 `f13940cd98dcdead…`)
- Peer ePaDEL wrapper `1.1.0` (anonymized)
- RDKit `2026.03.4`
- SMILES: `['CCO', 'c1ccccc1', 'CC(=O)O']`
- Tolerances: atol=1e-06, rtol=1e-06

## Results

### subset_ALOGP_Crippen_Weight

- Columns: padelpy2=7, peer=7, shared=7, only_padelpy2=0, only_peer=0
- Cells: exact=21, close=0, mismatch=0, nan_both=0, nan_xor=0
- Shared columns all close: **True**; column sets equal: **True**

### MACCS

- Columns: padelpy2=166, peer=166, shared=166, only_padelpy2=0, only_peer=0
- Cells: exact=498, close=0, mismatch=0, nan_both=0, nan_xor=0
- Shared columns all close: **True**; column sets equal: **True**

### descriptors_2d_catalogs

- Columns: padelpy2=1444, peer=1444, shared=1444, only_padelpy2=0, only_peer=0
- Cells: exact=4098, close=10, mismatch=223, nan_both=1, nan_xor=0
- Shared columns all close: **False**; column sets equal: **True**
- mismatch sample: `[{'row': 1, 'col': 'EE_DzZ', 'padelpy2': 6.845495371866151, 'peer': 6.009012618906293, 'abs_diff': 0.8364827529598582, 'kind': 'value'}, {'row': 1, 'col': 'EE_Dze', 'padelpy2': 6.845495371866151, 'peer': 6.009012618906293, 'abs_diff': 0.8364827529598582, 'kind': 'value'}, {'row': 1, 'col': 'EE_Dzi', 'padelpy2': 6.845495371866151, 'peer': 6.009012618906293, 'abs_diff': 0.8364827529598582, 'kind': 'value'}, {'row': 1, 'col': 'EE_Dzm', 'padelpy2': 6.845495371866151, 'peer': 6.009012618906293, 'abs_diff': 0.8364827529598582, 'kind': 'value'}, {'row': 1, 'col': 'EE_Dzp', 'padelpy2': 6.845495371866151, 'peer': 6.009012618906293, 'abs_diff': 0.8364827529598582, 'kind': 'value'}]`

## Verdict

**PARTIAL — supports §3.2 (narrow & differentiate)**

Core subset (ALOGP/Crippen/Weight) and MACCS are **bit-exact** on all three molecules. Full 2D catalogs share the same 1444 column names, but **223 cells disagree**, and **all disagreements are on benzene** (`c1ccccc1`). Ethanol and acetic acid match within tolerance on every 2D column.

Disagreeing columns include aromatic counts (`naAromAtom`, `nAromBond`) and many topological/Barysz-style families (`Sp*`, `EE_*`, `VE*`, `VR*`, `ETA`, …). This is consistent with **different aromaticity / graph handling between the stock Yap JAR and ePaDEL**, not random noise.

**Implication for design:** Classic stock-JAR fidelity is a real product distinction for aromatic molecules. Continue padelpy2 under §3.2 (stock JAR + padelpy continuity + oracles). Do not pivot solely on Calculator ergonomics. Re-run a peer comparison only if the stock JAR or a peer ePaDEL bundle changes and maintainers need a refreshed archive.

## How to reproduce

The original comparison script has been removed so this repository does not
advertise or depend on a named peer package. Machine-readable results remain in
`parity_report.json` and the CSV artifacts in this directory. To refresh a
similar study, compare padelpy2 stock-JAR outputs to any ePaDEL-family engine
on the same SMILES list and tolerances, then update this archive deliberately.

## Artifacts

- JSON: `docs/design/parity_g0/parity_report.json`
- CSVs: `docs/design/parity_g0/*.csv`
