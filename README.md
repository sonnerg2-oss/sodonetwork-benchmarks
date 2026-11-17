# SodoNetwork Benchmarks — Reproducible Mutation Guard Evaluation

[![PyPI version](https://img.shields.io/pypi/v/sodonetwork.svg)](https://pypi.org/project/sodonetwork/)
[![Reproducible Benchmark CI](https://github.com/sonnerg2-oss/sodonetwork-benchmarks/actions/workflows/benchmark.yml/badge.svg)](https://github.com/sonnerg2-oss/sodonetwork-benchmarks/actions/workflows/benchmark.yml)

Independent, reproducible benchmark suite evaluating **`sodonetwork`** (`verify_code_mutation_integrity`) against static compiler checks (`python -m py_compile`) on real third-party Python Standard Library source files.

> **Core Thesis:** *"We don't control what AI thinks; we control how it behaves in enterprise environments."*

---

## Why This Repository Exists

Most AI tooling claims rely on cherry-picked demos or self-referential metrics. This repository is designed to avoid self-benchmarking bias:

1. **Third-Party Corpus:** Uses 20 real modules from Python's own Standard Library (`json`, `http`, `urllib`, `email`, `argparse`, `pathlib`, `logging`, `subprocess`, `shutil`, `ast`, `sqlite3`, etc.) — available natively on every developer machine and GitHub Actions runner.
2. **AST-Valid Defect Injection:** Every synthetic defect (`lazy_truncation`, `destructive_shrink`, `empty_wipe`) is parsed with `ast.parse()` so it stays **100% syntactically valid Python**. Static compilers (`py_compile`) fail silently (`Exit Code 0`) on every single one of these defects.
3. **Non-Shrinking Isolation:** Lazy placeholder comment variants are tested *without* triggering >35% file-size shrinkage so phrase-detection recall and false negatives are measured honestly.
4. **Full Failure Transparency:** Missed variants (False Negatives) and edge-case gaps in `sodonetwork==3.6.1` are published openly alongside passing results.

---

## Results Progression: `v3.6.1` Baseline → `v3.6.2` Hardened (`220` Identical AST-Valid Cases)

> Full reproducible output (`v3.6.2`): [`results/BENCHMARK_REPORT.md`](results/BENCHMARK_REPORT.md) | Raw JSON: [`results/latest_results.json`](results/latest_results.json) | Case-by-case CSV: [`results/latest_cases.csv`](results/latest_cases.csv)

| Metric | Control (`py_compile` alone) | `sodonetwork==3.6.1` (Baseline) | `sodonetwork==3.6.2` (Hardened) |
| :--- | :---: | :---: | :---: |
| AST-Valid Defect Cases Evaluated | 180 | 180 | 180 |
| Defects Silently Passed | **180 / 180 (100.0%)** | 60 / 180 | **0 / 180** |
| Defects Blocked (Recall / TPR) | 0 / 180 (0.0%) | 120 / 180 (66.67%) | **180 / 180 (100.0%)** |
| Benign Edits Blocked (False Positives) | — | **0 / 40 (0.0% FPR)** | **0 / 40 (0.0% FPR)** |
| Precision | — | 100.0% | **100.0%** |
| Median Latency (`p50`) | 56.811 ms | 0.771 ms | **0.962 ms** |
| Tail Latency (`p95`) | 70.171 ms | 3.630 ms | **4.505 ms** |

### How Benchmark Evidence Drove `v3.6.2`
Running the `v3.6.1` suite uncovered **3 real detection blind spots** when LLM truncation did not shrink file size by >35%:
1. `variant_omitted_brevity` (`# ... omitted for brevity ...`) — `0/20` (`v3.6.1`) → **`20/20`** (`v3.6.2`)
2. `variant_methods_unchanged` (`# ... other helper methods remain unchanged ...`) — `0/20` (`v3.6.1`) → **`20/20`** (`v3.6.2`)
3. `variant_inline_comment` (`x = True  # rest of code unchanged`) — `0/20` (`v3.6.1`) → **`20/20`** (`v3.6.2`)

In `v3.6.2`, `verify_code_mutation_integrity` was upgraded to strip quoted string literals safely before scanning both full-line and inline trailing comments, closing all 3 gaps while keeping **False Positives at 0/40 (0.0%)** across all 20 Python stdlib modules.

---

## Reproduce Locally in 30 Seconds

```bash
git clone https://github.com/sonnerg2-oss/sodonetwork-benchmarks.git
cd sodonetwork-benchmarks
pip install sodonetwork==3.6.2
python benchmarks/run_benchmark.py
```

Raw outputs will be written to `results/latest_results.json`, `results/latest_cases.csv`, and `results/BENCHMARK_REPORT.md`.

---

## Author & Governance Reference

- **Author:** Soner DÖNMEZ ([LinkedIn](https://www.linkedin.com/in/soner-donmez-9a45255b) | `sonerdonmez@hotmail.com.tr`)
- **Official PyPI Package:** [`sodonetwork`](https://pypi.org/project/sodonetwork/)
- **Copyright Registration:** Republic of Türkiye Ministry of Culture and Tourism No. `2026/21386`
