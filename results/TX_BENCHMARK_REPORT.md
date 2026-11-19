# SodoNetwork `v4.0.0` — Multi-File TX & Cross-Link Benchmark Report

- **Generated (UTC):** `2026-11-19T20:41:16.398683+00:00`
- **Environment:** `Windows 10` (`AMD64`) • Python `3.9.13`
- **Overall Result:** **`32 / 32` (`100.0%`)** • `p50 = 1.014 ms` • `p95 = 108.184 ms`

| Category | Passed / Total |
| :--- | :---: |
| `polyglot_hanging_code` | **7 / 7** |
| `polyglot_clean_control` | **7 / 7** |
| `cross_link_broken_blocked` | **6 / 6** |
| `cross_link_coordinated_pass` | **6 / 6** |
| `atomic_rollback` | **3 / 3** |
| `scope_and_honesty` | **3 / 3** |

## Case-by-Case Breakdown

| Category | Case | Expected | Result | Latency (ms) |
| :--- | :--- | :---: | :---: | :---: |
| `polyglot_hanging_code` | `broken.kt` | `BLOCK` | **PASS** | 0.191 |
| `polyglot_hanging_code` | `broken.ts` | `BLOCK` | **PASS** | 0.184 |
| `polyglot_hanging_code` | `broken.go` | `BLOCK` | **PASS** | 0.172 |
| `polyglot_hanging_code` | `broken.rs` | `BLOCK` | **PASS** | 0.18 |
| `polyglot_hanging_code` | `broken.php` | `BLOCK` | **PASS** | 0.179 |
| `polyglot_hanging_code` | `broken.json` | `BLOCK` | **PASS** | 0.73 |
| `polyglot_hanging_code` | `broken.py` | `BLOCK` | **PASS** | 0.947 |
| `polyglot_clean_control` | `clean.kt` | `PASS` | **PASS** | 0.687 |
| `polyglot_clean_control` | `clean.ts` | `PASS` | **PASS** | 0.488 |
| `polyglot_clean_control` | `clean.go` | `PASS` | **PASS** | 0.451 |
| `polyglot_clean_control` | `clean.rs` | `PASS` | **PASS** | 0.777 |
| `polyglot_clean_control` | `clean.php` | `PASS` | **PASS** | 0.745 |
| `polyglot_clean_control` | `clean.json` | `PASS` | **PASS** | 0.514 |
| `polyglot_clean_control` | `clean.py` | `PASS` | **PASS** | 0.637 |
| `cross_link_broken_blocked` | `typescript:x_auth.ts->x_checkout.ts` | `BLOCK` | **PASS** | 7.064 |
| `cross_link_coordinated_pass` | `typescript:x_auth.ts+x_checkout.ts` | `PASS` | **PASS** | 5.459 |
| `cross_link_broken_blocked` | `python:x_billing.py->x_api.py` | `BLOCK` | **PASS** | 60.215 |
| `cross_link_coordinated_pass` | `python:x_billing.py+x_api.py` | `PASS` | **PASS** | 108.184 |
| `cross_link_broken_blocked` | `php:x_ledger.php->x_handler.php` | `BLOCK` | **PASS** | 74.319 |
| `cross_link_coordinated_pass` | `php:x_ledger.php+x_handler.php` | `PASS` | **PASS** | 132.174 |
| `cross_link_broken_blocked` | `kotlin:XTokenGuard.kt->XCheckoutScreen.kt` | `BLOCK` | **PASS** | 6.034 |
| `cross_link_coordinated_pass` | `kotlin:XTokenGuard.kt+XCheckoutScreen.kt` | `PASS` | **PASS** | 6.74 |
| `cross_link_broken_blocked` | `go:x_signer.go->x_router.go` | `BLOCK` | **PASS** | 6.7 |
| `cross_link_coordinated_pass` | `go:x_signer.go+x_router.go` | `PASS` | **PASS** | 6.894 |
| `cross_link_broken_blocked` | `rust:x_vault.rs->x_worker.rs` | `BLOCK` | **PASS** | 6.651 |
| `cross_link_coordinated_pass` | `rust:x_vault.rs+x_worker.rs` | `PASS` | **PASS** | 7.174 |
| `atomic_rollback` | `multi_file_sha256_restore` | `RESTORE_EXACT` | **PASS** | 2.989 |
| `atomic_rollback` | `orphan_new_file_cleanup` | `DELETED` | **PASS** | 2.989 |
| `atomic_rollback` | `commit_auto_rollback_on_hanging_code` | `AUTO_ROLLED_BACK` | **PASS** | 7.699 |
| `scope_and_honesty` | `forbidden_scope:core/data/secret.py` | `BLOCK` | **PASS** | 1.014 |
| `scope_and_honesty` | `forbidden_scope:infra/deploy.yml` | `BLOCK` | **PASS** | 0.853 |
| `scope_and_honesty` | `honest_queue_unverified_no_fake_ast` | `UNVERIFIED` | **PASS** | 0.501 |
