# Stock-JAR oracles v1

Regression fixtures that pin **classic Yap PaDEL-Descriptor** outputs for
`padelpy2`. These are **package-generated** golden values (not literature table
extractions). Outputs from other PaDEL-family distributions must not be used as
oracles.

## Identity

| Field | Value |
|-------|--------|
| Oracle id | `oracles_v1` |
| Engine | Stock `PaDEL-Descriptor.jar` (Yap, 2011) |
| JAR path | `padelpy2/PaDEL-Descriptor/PaDEL-Descriptor.jar` |
| JAR sha256 | `f13940cd98dcdeadc54124f4111081c740fcc6effbfa33cf494125b707cad133` |
| padelpy2 version (generated) | `0.1.0` |
| RDKit version (generated) | `2026.03.4` |
| Kind | `regression` |

## Molecules (row order)

| Row | SMILES | Notes |
|-----|--------|--------|
| 0 | `CCO` | Ethanol |
| 1 | `c1ccccc1` | Benzene — aromatic sentinels (stock defaults) |
| 2 | `CC(=O)O` | Acetic acid |

## Preparation and flags

- RDKit: `MolFromSmiles` → `AddHs`
- 2D / fingerprints: `Compute2DCoords`
- 3D: `EmbedMolecule(..., randomSeed=0xC0FFEE)` (`12648430`)
- `PaDELConfig(threads=1)` for deterministic PaDEL workers (`detectaromaticity=False`, other defaults)
- Output: `Name` column dropped (package default)
- Float compare: `atol=1e-6`, `rtol=1e-6` (NaN-aware)

## Artifacts

| File | Content | Shape (rows × cols) |
|------|---------|---------------------|
| `subset_2d.csv` | ALOGP + Crippen + Weight | 3 × 7 |
| `descriptors_2d.csv` | Default 2D catalog | 3 × 1444 |
| `maccs.csv` | MACCS fingerprints | 3 × 166 |
| `descriptors_3d.csv` | Default 3D catalog | 3 × 431 |
| `benzene_aromatic_sentinels.json` | Benzene values for drift-sensitive columns | — |
| `meta.json` | Machine-readable card fields | — |

## Benzene aromatic sentinels

Stock JAR (default config) yields `naAromAtom=0` and `nAromBond=0` for benzene.
Sentinel columns also include topology descriptors that drifted in the historical
G0 peer comparison (`SpAbs_DzZ`, `EE_DzZ`, `VE1_DzZ`, `ETA_Beta`). Tests fail if
these drift. See `docs/design/parity_g0/PARITY.md` for the archive.

## Citation (engine identity)

Yap, C. W. (2011). PaDEL-Descriptor: An open source software to calculate
molecular descriptors and fingerprints. *Journal of Computational Chemistry*,
32(7), 1466–1474. https://doi.org/10.1002/jcc.21707

## License and limitations

- Fixtures are derived from the vendored PaDEL-Descriptor engine shipped with
  this package; redistributed under the same terms as the package `LICENSE`.
- Values depend on stock JAR bytes, default config flags, RDKit prep, and (for
  3D) the documented embed seed. Do not treat as universal chemical ground truth.
- Not interchangeable with other PaDEL-family distributions without verification.

## Regeneration

Requires Java (JRE 8+), RDKit, and an editable install of `padelpy2`:

```bash
python scripts/generate_oracles_v1.py
```

After regenerating, confirm `meta.json` / this card still list the same JAR
sha256 as the vendored file (or update both deliberately if the JAR changes).
