#!/usr/bin/env python3
"""G3 timing benchmarks: cold vs chunked padelpy2 (optional padelpy)."""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from padelpy2 import Calculator
from padelpy2.config import PaDELConfig
from padelpy2.descriptors import Weight
from padelpy2.wrapper import PADEL_PATH
from rdkit import Chem
from rdkit.Chem import AllChem

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "design" / "benchmarks_g3"
BASE_SMILES = "CCO"


def jar_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_mols(n: int) -> list:
    mols = []
    for _ in range(n):
        mol = Chem.AddHs(Chem.MolFromSmiles(BASE_SMILES))
        AllChem.Compute2DCoords(mol)
        mols.append(mol)
    return mols


def timed(fn) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def bench_padelpy2(n: int, chunk_size: int | None) -> dict:
    cfg = PaDELConfig(threads=1)
    calc = Calculator([Weight], config=cfg)
    mols = make_mols(n)

    def run_once():
        if chunk_size is None:
            calc(mols)
        else:
            calc(mols, chunk_size=chunk_size)

    cold = timed(run_once)
    second = timed(run_once)
    return {
        "engine": "padelpy2",
        "n": n,
        "chunk_size": chunk_size,
        "cold_s": round(cold, 4),
        "second_call_s": round(second, 4),
        "note": (
            "second_call is a new java -jar process (OS/page-cache warm), "
            "not JVM keep-alive"
        ),
    }


def bench_padelpy(n: int) -> dict | None:
    try:
        from padelpy import from_smiles
    except ImportError:
        return None
    smiles = [BASE_SMILES] * n

    def run_once():
        from_smiles(smiles, fingerprints=False, timeout=None)

    cold = timed(run_once)
    second = timed(run_once)
    return {
        "engine": "padelpy",
        "n": n,
        "chunk_size": None,
        "cold_s": round(cold, 4),
        "second_call_s": round(second, 4),
        "note": "padelpy from_smiles list; stock JAR family",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sizes",
        default="10,100",
        help="Comma-separated molecule counts (default: 10,100)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=25,
        help="chunk_size for padelpy2 chunked runs (default: 25)",
    )
    parser.add_argument(
        "--large",
        action="store_true",
        help="Also run n=1000",
    )
    parser.add_argument(
        "--padelpy",
        action="store_true",
        help="Compare padelpy if installed",
    )
    args = parser.parse_args()

    sizes = [int(x) for x in args.sizes.split(",") if x.strip()]
    if args.large and 1000 not in sizes:
        sizes.append(1000)

    try:
        pkg_ver = version("padelpy2")
    except PackageNotFoundError:
        pkg_ver = "0.1.0"

    rows = []
    for n in sizes:
        rows.append(bench_padelpy2(n, chunk_size=None))
        rows.append(bench_padelpy2(n, chunk_size=args.chunk_size))
        if args.padelpy:
            result = bench_padelpy(n)
            if result:
                rows.append(result)

    meta = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "padelpy2_version": pkg_ver,
        "stock_jar_sha256": jar_sha256(Path(PADEL_PATH)),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "rdkit_version": Chem.rdBase.rdkitVersion,
        "java_note": "system java on PATH; each padeldescriptor starts a new JVM",
        "jvm_reuse": "deferred — stock CLI JAR has no keep-alive / worker protocol",
        "base_smiles": BASE_SMILES,
        "descriptor": "Weight",
        "padel_threads": 1,
        "sizes": sizes,
        "chunk_size": args.chunk_size,
    }
    payload = {"meta": meta, "results": rows}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "RESULTS.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# G3 timing snapshot",
        "",
        f"- Date (UTC): `{meta['date_utc']}`",
        f"- padelpy2: `{meta['padelpy2_version']}`",
        f"- Platform: `{meta['platform']}`",
        f"- Processor: `{meta['processor']}`",
        f"- Python: `{meta['python']}`; RDKit: `{meta['rdkit_version']}`",
        f"- Stock JAR sha256: `{meta['stock_jar_sha256']}`",
        f"- Molecules: ethanol (`{BASE_SMILES}`) × N; descriptor: Weight; "
        f"`PaDELConfig(threads=1)`",
        f"- Chunk size (padelpy2 chunked rows): `{args.chunk_size}`",
        "",
        "## JVM reuse decision",
        "",
        "Deferred. Each `padeldescriptor` call runs `java -jar` against the stock",
        "PaDEL-Descriptor CLI. The vendored JAR exposes no keep-alive worker API.",
        "True JVM reuse would require a custom long-lived process protocol (out of",
        "scope). UX parity for large lists is `Calculator(..., chunk_size=N)`.",
        "",
        "## Results (wall seconds)",
        "",
        "| Engine | N | chunk_size | cold_s | second_call_s |",
        "|--------|---|------------|--------|---------------|",
    ]
    for row in rows:
        chunk = row["chunk_size"] if row["chunk_size"] is not None else "—"
        lines.append(
            f"| {row['engine']} | {row['n']} | {chunk} | "
            f"{row['cold_s']} | {row['second_call_s']} |"
        )
    lines.extend(
        [
            "",
            "## Caveats",
            "",
            "- Numbers are machine-specific snapshots, not CI gates.",
            "- `second_call_s` is not JVM keep-alive; a new process starts each run.",
            "- Do not claim unique speed versus Mordred or other engines from these",
            "  figures.",
            "",
            "Regenerate::",
            "",
            "   python scripts/bench_padelpy2.py --sizes 10,100",
            "",
        ]
    )
    (OUT_DIR / "RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {OUT_DIR / 'RESULTS.md'}")


if __name__ == "__main__":
    main()
