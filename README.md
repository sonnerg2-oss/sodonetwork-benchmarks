# SodoNetwork Benchmarks — Reproducible Mutation Guard Evaluation

[![PyPI version](https://img.shields.io/pypi/v/sodonetwork.svg)](https://pypi.org/project/sodonetwork/)

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

## Baseline Results (`sodonetwork==3.6.1` on 220 AST-Valid Cases)

> Full reproducible output: [`results/BENCHMARK_REPORT.md`](results/BENCHMARK_REPORT.md) | Raw JSON: [`results/latest_results.json`](results/latest_results.json) | Case-by-case CSV: [`results/latest_cases.csv`](results/latest_cases.csv)

| Metric | Control (`py_compile` alone) | `sodonetwork==3.6.1` Guard |
| :--- | :---: | :---: |
| AST-Valid Defect Cases Evaluated | 180 | 180 |
| Defects Silently Passed | **180 / 180 (100.0%)** | **60 / 180** (False Negatives) |
| Defects Blocked (Recall / TPR) | 0 / 180 (0.0%) | **120 / 180 (66.67%)** |
| Benign Edits Blocked (False Positives) | — | **0 / 40 (0.0% FPR)** |
| Precision | — | **100.0%** |
| Median Latency (`p50`) | 55.484 ms | **0.771 ms** |
| Tail Latency (`p95`) | 61.613 ms | **3.630 ms** |

### Empirical Gaps Uncovered in `v3.6.1`
Running this independent benchmark immediately revealed **3 real detection blind spots** in `sodonetwork==3.6.1` when truncation does not also shrink file size by >35%:
1. `variant_omitted_brevity` (`# ... omitted for brevity ...`) — `0/20` blocked
2. `variant_methods_unchanged` (`# ... other helper methods remain unchanged ...`) — `0/20` blocked
3. `variant_inline_comment` (`x = True  # rest of code unchanged`) — `0/20` blocked (only full-line comments starting with `#` were checked)

These documented failure cases serve as the exact quantitative baseline for hardening `v3.6.2`.

---

## Reproduce Locally in 30 Seconds

```bash
git clone <THIS_REPO_URL>
cd sodonetwork-benchmarks
pip install sodonetwork==3.6.1
python benchmarks/run_benchmark.py
```

Raw outputs will be written to `results/latest_results.json`, `results/latest_cases.csv`, and `results/BENCHMARK_REPORT.md`.

---

## Author & Governance Reference

- **Author:** Soner DÖNMEZ ([LinkedIn](https://www.linkedin.com/in/soner-donmez-9a45255b) | `sonerdonmez@hotmail.com.tr`)
- **Official PyPI Package:** [`sodonetwork`](https://pypi.org/project/sodonetwork/)
- **Copyright Registration:** Republic of Türkiye Ministry of Culture and Tourism No. `2026/21386`
