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

## Results Progression: `v3.6.1` → `v3.6.2` → `v4.0.0` (`220` AST-Valid Stdlib Cases + `32` Multi-File TX Scenarios)

> Full reproducible outputs (`v4.0.0`): [`results/BENCHMARK_REPORT.md`](results/BENCHMARK_REPORT.md) | [`results/TX_BENCHMARK_REPORT.md`](results/TX_BENCHMARK_REPORT.md) | Raw JSON: [`results/latest_results.json`](results/latest_results.json) & [`results/tx_results.json`](results/tx_results.json)

### Suite 1 — Python Standard Library Mutation Guard (`220` AST-Valid Cases)

| Metric | Control (`py_compile` alone) | `sodonetwork==3.6.1` | `sodonetwork==3.6.2` | `sodonetwork==4.0.0` |
| :--- | :---: | :---: | :---: | :---: |
| AST-Valid Defect Cases Evaluated | 180 | 180 | 180 | **180** |
| Defects Silently Passed | **180 / 180 (100.0%)** | 60 / 180 | 0 / 180 | **0 / 180** |
| Defects Blocked (Recall / TPR) | 0 / 180 (0.0%) | 120 / 180 (66.67%) | 180 / 180 (100.0%) | **180 / 180 (100.0%)** |
| Benign Edits Blocked (FPR) | — | 0 / 40 (0.0%) | 0 / 40 (0.0%) | **0 / 40 (0.0%)** |
| Precision | — | 100.0% | 100.0% | **100.0%** |

### Suite 2 — `v4.0.0 TX` Update Architecture (`32` Multi-File & Polyglot Scenarios)

Tests `sodonetwork==4.0.0` across 7 languages (`.py`, `.ts`, `.php`, `.kt`, `.go`, `.rs`, `.json`) without requiring local language compilers:
- **`polyglot_hanging_code` (`7/7`):** Unclosed braces/brackets/comments caught across Kotlin, TypeScript, Go, Rust, PHP, JSON, and Python.
- **`polyglot_clean_control` (`7/7`):** `0%` false positives on valid polyglot code (including Rust lifetimes `'a`, template literals, PHP `#` comments, strings containing `{}`).
- **`cross_link_broken_blocked` (`6/6`):** Renaming/deleting an exported symbol in File A while File B still imports/calls it is blocked fail-closed across TypeScript, Python, PHP, Kotlin, Go, and Rust.
- **`cross_link_coordinated_pass` (`6/6`):** Staging and updating File B in the same transaction resolves cross-link references (`0` broken) and passes cleanly.
- **`atomic_rollback` (`3/3`):** Byte-exact SHA-256 restoration of modified files, orphan new file removal, and `--auto-rollback` on hanging-code commit failure.
- **`scope_and_honesty` (`3/3`):** `core/data/**` and `infra/**` blocked fail-closed; unmatched queue markers honestly reported as `UNVERIFIED`.

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
pip install sodonetwork==4.0.0
python benchmarks/run_benchmark.py
python benchmarks/run_tx_benchmark.py
```

Raw outputs will be written to `results/latest_results.json`, `results/latest_cases.csv`, and `results/BENCHMARK_REPORT.md`.

---

## Author & Governance Reference

- **Author:** Soner DÖNMEZ ([LinkedIn](https://www.linkedin.com/in/soner-donmez-9a45255b) | `sonerdonmez@hotmail.com.tr`)
- **Official PyPI Package:** [`sodonetwork`](https://pypi.org/project/sodonetwork/)
- **Copyright Registration:** Republic of Türkiye Ministry of Culture and Tourism No. `2026/21386`
