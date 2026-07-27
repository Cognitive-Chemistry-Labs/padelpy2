# G3 benchmark method

## Purpose

Measure wall-clock timing for padelpy2 stock-JAR `Calculator` paths after T2.1
(`chunk_size`), and record the JVM-reuse decision for G3.

## Workload

- Molecule: ethanol (`CCO`), RDKit `AddHs` + `Compute2DCoords`, repeated N times
- Descriptor catalog: `Weight` only (small, stable)
- Config: `PaDELConfig(threads=1)`
- Sizes: N = 10 and 100 by default; N = 1000 via `--large`
- Chunked path: `chunk_size=25` (default CLI flag)

## Metrics

| Label | Meaning |
|-------|---------|
| `cold_s` | First timed call in the process for that configuration |
| `second_call_s` | Immediately repeated call (new `java -jar` each time) |

`second_call_s` reflects OS/page-cache effects only. It is **not** JVM keep-alive.

## JVM reuse

**Deferred.** The stock PaDEL-Descriptor CLI is started with `java -jar` per
`padeldescriptor` invocation. The vendored JAR does not expose a keep-alive or
worker protocol. Implementing reuse would require a custom long-lived bridge.
Large-list UX remains `Calculator(..., chunk_size=N)`, noting that each chunk
currently starts a new JVM (chunking can increase wall time for small catalogs
while bounding peak batch size).

## Optional compares

- `--padelpy`: `padelpy.from_smiles` (default full descriptor set — not
  Weight-only; interpret carefully)

## Regeneration

```bash
python scripts/bench_padelpy2.py --sizes 10,100
```

Outputs: `RESULTS.json`, `RESULTS.md` in this directory.
