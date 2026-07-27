# G3 timing snapshot

- Date (UTC): `2026-07-27T16:26:24.886428+00:00`
- padelpy2: `0.1.0`
- Platform: `macOS-26.5.1-arm64-arm-64bit`
- Processor: `arm`
- Python: `3.11.8`; RDKit: `2026.03.4`
- Stock JAR sha256: `f13940cd98dcdeadc54124f4111081c740fcc6effbfa33cf494125b707cad133`
- Molecules: ethanol (`CCO`) × N; descriptor: Weight; `PaDELConfig(threads=1)`
- Chunk size (padelpy2 chunked rows): `25`

## JVM reuse decision

Deferred. Each `padeldescriptor` call runs `java -jar` against the stock
PaDEL-Descriptor CLI. The vendored JAR exposes no keep-alive worker API.
True JVM reuse would require a custom long-lived process protocol (out of
scope). UX parity for large lists is `Calculator(..., chunk_size=N)`.

## Results (wall seconds)

| Engine | N | chunk_size | cold_s | second_call_s |
|--------|---|------------|--------|---------------|
| padelpy2 | 10 | — | 0.886 | 0.7109 |
| padelpy2 | 10 | 25 | 0.6968 | 0.7087 |
| padelpy2 | 100 | — | 0.8125 | 0.8244 |
| padelpy2 | 100 | 25 | 2.9013 | 2.9238 |

## Caveats

- Numbers are machine-specific snapshots, not CI gates.
- `second_call_s` is not JVM keep-alive; a new process starts each run.
- Do not claim unique speed versus Mordred or other engines from these
  figures.

Regenerate::

   python scripts/bench_padelpy2.py --sizes 10,100
