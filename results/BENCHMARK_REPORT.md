# SodoNetwork Independent Benchmark Report

- **Timestamp (UTC):** `2026-11-17T22:28:29.063269+00:00`
- **Package Version:** `sodonetwork==3.6.2`
- **Environment:** Python `3.9.13` on `Windows 10` (`AMD64`)
- **Independent Corpus:** `20` real Python Standard Library files (`total 220 AST-valid mutated test cases`)

## Control (`py_compile` alone) vs. `sodonetwork` Mutation Guard

| Metric | Control (`py_compile` alone) | SodoNetwork Guard (`verify_code_mutation_integrity`) |
| :--- | :---: | :---: |
| Defect Cases Evaluated (All AST-Valid) | 180 | 180 |
| Defects Silently Passed | **180** (100.0%) | **0** (False Negatives) |
| Defects Blocked (Recall / TPR) | 0 | **180/180 (100.0%)** |
| Benign Clean Edits (False Positives) | — | **0/40 (0.0% FPR)** |
| Precision | — | **100.0%** |
| Latency p50 | 57.206 ms | **2.041 ms** |
| Latency p95 | 66.045 ms | **11.637 ms** |

## Per-Variant Breakdown (Including Real Detection Gaps)

| Category :: Variant | Cases | `py_compile` Passed Silently | SodoNetwork Blocked |
| :--- | :---: | :---: | :---: |
| `benign_clean_edit::append_helper` | 20 | 20/20 | 0/20 |
| `benign_clean_edit::moderate_valid_trim_under_35pct` | 20 | 20/20 | 0/20 |
| `lazy_truncation_no_shrink::known_rest_of_code` | 20 | 20/20 | 20/20 |
| `lazy_truncation_no_shrink::known_existing_code` | 20 | 20/20 | 20/20 |
| `lazy_truncation_no_shrink::known_remaining_unchanged` | 20 | 20/20 | 20/20 |
| `lazy_truncation_no_shrink::known_impl_unchanged` | 20 | 20/20 | 20/20 |
| `lazy_truncation_no_shrink::variant_omitted_brevity` | 20 | 20/20 | 20/20 |
| `lazy_truncation_no_shrink::variant_methods_unchanged` | 20 | 20/20 | 20/20 |
| `lazy_truncation_no_shrink::variant_inline_comment` | 20 | 20/20 | 20/20 |
| `destructive_shrink::ast_valid_mass_delete` | 20 | 20/20 | 20/20 |
| `empty_wipe::whitespace_only` | 20 | 20/20 | 20/20 |

## Reproducibility
```bash
pip install sodonetwork==3.6.2
python benchmarks/run_benchmark.py
```
