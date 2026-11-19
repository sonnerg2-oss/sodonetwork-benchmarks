#!/usr/bin/env python3
"""
SodoNetwork v4.0 TX Update Architecture Benchmark
=================================================
Reproducible multi-language & multi-file benchmark testing the official PyPI
`sodonetwork` package across:
  1. Polyglot Hanging-Code & Structural Balance Guard (7 languages, no compiler)
  2. Language-Agnostic Cross-Link Broken Reference Gate (6 languages: TS, Py, PHP, Kotlin, Go, Rust)
  3. Atomic Multi-File Snapshot Rollback & Auto-Rollback (byte-exact SHA-256 verification)
  4. Fail-Closed Scope Lock & Honest Queue Reporting

Outputs `results/tx_results.json` and `results/TX_BENCHMARK_REPORT.md`.
"""

import argparse
import hashlib
import json
import os
import platform
import tempfile
import time
from datetime import datetime, timezone

import sodonetwork
import sodonetwork.cli as sodo


def sha256_file(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def run_suite(out_dir: str) -> int:
    os.makedirs(out_dir, exist_ok=True)
    records = []

    with tempfile.TemporaryDirectory() as ws:
        orig = (
            sodo.SCRIPT_DIR,
            sodo.CACHE_DIR,
            sodo.TOKEN_CACHE_FILE,
            sodo.TX_ROOT_DIR,
            sodo.ACTIVE_TX_FILE,
        )
        try:
            sodo.SCRIPT_DIR = ws
            sodo.CACHE_DIR = os.path.join(ws, ".sodonetwork")
            sodo.TOKEN_CACHE_FILE = os.path.join(sodo.CACHE_DIR, ".active_session.json")
            sodo.TX_ROOT_DIR = os.path.join(sodo.CACHE_DIR, "tx")
            sodo.ACTIVE_TX_FILE = os.path.join(sodo.TX_ROOT_DIR, "active_tx.json")

            # ------------------------------------------------------------------
            # 1. Polyglot Structural Balance & Hanging-Code Guard (14 cases)
            # ------------------------------------------------------------------
            polyglot_broken = {
                "broken.kt": "class Auth {\n    fun login(u: String) {\n        println(u)\n",
                "broken.ts": "export function verifyToken(t: string): boolean {\n  if (t.length > 0) {\n    return true;\n",
                "broken.go": 'package main\nfunc serve() {\n    x := "{not a brace}"\n',
                "broken.rs": "pub fn parse<'a>(s: &'a str) -> &'a str { /* unclosed comment\n  s\n}\n",
                "broken.php": "<?php\nfunction handle($x) {\n  # comment with }\n  if ($x) {\n    return 1;\n}\n",
                "broken.json": '{"name": "sodo", "version": 4',
                "broken.py": "def broken(a, b):\n    x = [1, 2, 3\n    return x\n",
            }
            for fname, code in polyglot_broken.items():
                p = os.path.join(ws, fname)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(code)
                t0 = time.perf_counter()
                res = sodo.verify_code_mutation_integrity(p, None)
                ms = (time.perf_counter() - t0) * 1000.0
                records.append({
                    "category": "polyglot_hanging_code",
                    "case": fname,
                    "expected": "BLOCK",
                    "passed_assertion": not res.get("passed", True),
                    "latency_ms": round(ms, 3),
                })

            polyglot_clean = {
                "clean.kt": 'class Auth {\n    fun login(u: String): String {\n        val msg = "{hello}"\n        return msg\n    }\n}\n',
                "clean.ts": 'export function verifyToken(t: string): boolean {\n  const s = `template ${t} }`;\n  return s.length > 0;\n}\n',
                "clean.go": 'package main\nfunc serve() string {\n    return "{ok}"\n}\n',
                "clean.rs": "pub fn first<'a>(s: &'a str) -> &'a str {\n    let ch = '{';\n    let _ = ch;\n    s\n}\n",
                "clean.php": "<?php\nfunction handle($x) {\n  # comment with }\n  return '{ok}';\n}\n",
                "clean.json": '{"name": "sodo", "version": 4}\n',
                "clean.py": "def ok(a, b):\n    return {'sum': a + b}\n",
            }
            for fname, code in polyglot_clean.items():
                p = os.path.join(ws, fname)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(code)
                t0 = time.perf_counter()
                res = sodo.verify_code_mutation_integrity(p, None)
                ms = (time.perf_counter() - t0) * 1000.0
                records.append({
                    "category": "polyglot_clean_control",
                    "case": fname,
                    "expected": "PASS",
                    "passed_assertion": bool(res.get("passed", False)),
                    "latency_ms": round(ms, 3),
                })

            # ------------------------------------------------------------------
            # 2. Language-Agnostic Cross-Link Broken Reference Gate (12 cases)
            # ------------------------------------------------------------------
            cross_scenarios = [
                (
                    "typescript",
                    "x_auth.ts",
                    "x_checkout.ts",
                    "export function verifySessionToken(t: string): boolean {\n  return t.length > 0;\n}\n",
                    "export function verifySessionV2(t: string): boolean {\n  return t.length > 0;\n}\n",
                    "import { verifySessionToken } from './x_auth';\nexport function runPay(t: string) {\n  return verifySessionToken(t);\n}\n",
                    "import { verifySessionV2 } from './x_auth';\nexport function runPay(t: string) {\n  return verifySessionV2(t);\n}\n",
                    "verifySessionToken",
                ),
                (
                    "python",
                    "x_billing.py",
                    "x_api.py",
                    "def computeInvoiceTax(amount):\n    return round(amount * 0.2, 2)\n",
                    "def computeInvoiceTaxV2(amount):\n    return round(amount * 0.2, 2)\n",
                    "from x_billing import computeInvoiceTax\ndef handle_order(a):\n    return computeInvoiceTax(a)\n",
                    "from x_billing import computeInvoiceTaxV2\ndef handle_order(a):\n    return computeInvoiceTaxV2(a)\n",
                    "computeInvoiceTax",
                ),
                (
                    "php",
                    "x_ledger.php",
                    "x_handler.php",
                    "<?php\nfunction sealLedgerHash($val) {\n    return hash('sha256', $val);\n}\n",
                    "<?php\nfunction sealLedgerHashV2($val) {\n    return hash('sha256', $val);\n}\n",
                    "<?php\nrequire_once 'x_ledger.php';\nfunction runSeal($v) {\n    return sealLedgerHash($v);\n}\n",
                    "<?php\nrequire_once 'x_ledger.php';\nfunction runSeal($v) {\n    return sealLedgerHashV2($v);\n}\n",
                    "sealLedgerHash",
                ),
                (
                    "kotlin",
                    "XTokenGuard.kt",
                    "XCheckoutScreen.kt",
                    "class XTokenGuard {\n    fun validateCapabilityToken(t: String): Boolean {\n        return t.isNotEmpty()\n    }\n}\n",
                    "class XTokenGuard {\n    fun validateCapabilityV2(t: String): Boolean {\n        return t.isNotEmpty()\n    }\n}\n",
                    "fun submitOrder(g: XTokenGuard, t: String): Boolean {\n    return g.validateCapabilityToken(t)\n}\n",
                    "fun submitOrder(g: XTokenGuard, t: String): Boolean {\n    return g.validateCapabilityV2(t)\n}\n",
                    "validateCapabilityToken",
                ),
                (
                    "go",
                    "x_signer.go",
                    "x_router.go",
                    "package app\nfunc VerifyPayloadSig(b string) bool {\n    return len(b) > 0\n}\n",
                    "package app\nfunc VerifyPayloadSigV2(b string) bool {\n    return len(b) > 0\n}\n",
                    "package app\nfunc HandleRoute(b string) bool {\n    return VerifyPayloadSig(b)\n}\n",
                    "package app\nfunc HandleRoute(b string) bool {\n    return VerifyPayloadSigV2(b)\n}\n",
                    "VerifyPayloadSig",
                ),
                (
                    "rust",
                    "x_vault.rs",
                    "x_worker.rs",
                    "pub fn seal_audit_frame(s: &str) -> bool {\n    !s.is_empty()\n}\n",
                    "pub fn seal_audit_frame_v2(s: &str) -> bool {\n    !s.is_empty()\n}\n",
                    "pub fn run_job(s: &str) -> bool {\n    seal_audit_frame(s)\n}\n",
                    "pub fn run_job(s: &str) -> bool {\n    seal_audit_frame_v2(s)\n}\n",
                    "seal_audit_frame",
                ),
            ]

            for lang, f_a, f_b, a_v1, a_v2, b_v1, b_v2, old_sym in cross_scenarios:
                p_a = os.path.join(ws, f_a)
                p_b = os.path.join(ws, f_b)
                with open(p_a, "w", encoding="utf-8") as f:
                    f.write(a_v1)
                with open(p_b, "w", encoding="utf-8") as f:
                    f.write(b_v1)

                sodo.tx_begin([f_a], prompt=f"Rename {old_sym}", offline=True, return_dict=True)
                with open(p_a, "w", encoding="utf-8") as f:
                    f.write(a_v2)

                t0 = time.perf_counter()
                v_broken = sodo.tx_verify(return_dict=True)
                ms_broken = (time.perf_counter() - t0) * 1000.0
                caught_broken = (
                    v_broken.get("status") == "TX_VERIFY_FAILED"
                    and any(
                        x.get("symbol") == old_sym and x.get("referenced_in") == f_b
                        for x in v_broken.get("broken_cross_links", [])
                    )
                )
                records.append({
                    "category": "cross_link_broken_blocked",
                    "case": f"{lang}:{f_a}->{f_b}",
                    "expected": "BLOCK",
                    "passed_assertion": caught_broken,
                    "latency_ms": round(ms_broken, 3),
                })

                # Now stage & update neighbor in same TX -> MUST PASS!
                sodo.tx_stage([f_b], return_dict=True)
                with open(p_b, "w", encoding="utf-8") as f:
                    f.write(b_v2)
                t1 = time.perf_counter()
                v_fixed = sodo.tx_verify(return_dict=True)
                ms_fixed = (time.perf_counter() - t1) * 1000.0
                records.append({
                    "category": "cross_link_coordinated_pass",
                    "case": f"{lang}:{f_a}+{f_b}",
                    "expected": "PASS",
                    "passed_assertion": (
                        v_fixed.get("status") == "TX_VERIFIED"
                        and v_fixed.get("cross_refs_broken") == 0
                    ),
                    "latency_ms": round(ms_fixed, 3),
                })
                sodo.tx_rollback(return_dict=True)

            # ------------------------------------------------------------------
            # 3. Atomic Rollback & Auto-Rollback (3 cases)
            # ------------------------------------------------------------------
            rb_a = os.path.join(ws, "x_auth.ts")
            rb_b = os.path.join(ws, "x_checkout.ts")
            rb_new = os.path.join(ws, "x_orphan_new.ts")
            sha_a0 = sha256_file(rb_a)
            sha_b0 = sha256_file(rb_b)

            sodo.tx_begin(["x_auth.ts", "x_checkout.ts"], prompt="Rollback test", offline=True, return_dict=True)
            sodo.tx_stage(["x_orphan_new.ts"], return_dict=True)
            with open(rb_a, "w", encoding="utf-8") as f:
                f.write("export function corrupted() {\n")
            with open(rb_b, "w", encoding="utf-8") as f:
                f.write("// wiped\n")
            with open(rb_new, "w", encoding="utf-8") as f:
                f.write("export function orphan() { return 1; }\n")

            t0 = time.perf_counter()
            rb_res = sodo.tx_rollback(return_dict=True)
            ms_rb = (time.perf_counter() - t0) * 1000.0
            records.append({
                "category": "atomic_rollback",
                "case": "multi_file_sha256_restore",
                "expected": "RESTORE_EXACT",
                "passed_assertion": (
                    rb_res.get("status") in ("TX_ROLLED_BACK", "ROLLED_BACK")
                    and sha256_file(rb_a) == sha_a0
                    and sha256_file(rb_b) == sha_b0
                ),
                "latency_ms": round(ms_rb, 3),
            })
            records.append({
                "category": "atomic_rollback",
                "case": "orphan_new_file_cleanup",
                "expected": "DELETED",
                "passed_assertion": not os.path.exists(rb_new),
                "latency_ms": round(ms_rb, 3),
            })

            sodo.tx_begin(["x_auth.ts"], prompt="Auto rollback test", offline=True, return_dict=True)
            with open(rb_a, "w", encoding="utf-8") as f:
                f.write("export function hanging() {\n  if (true) {\n")
            t0 = time.perf_counter()
            auto_rb = sodo.tx_commit(auto_rollback=True, return_dict=True)
            ms_arb = (time.perf_counter() - t0) * 1000.0
            records.append({
                "category": "atomic_rollback",
                "case": "commit_auto_rollback_on_hanging_code",
                "expected": "AUTO_ROLLED_BACK",
                "passed_assertion": (
                    auto_rb.get("status") in ("TX_ROLLED_BACK", "ROLLED_BACK")
                    and sha256_file(rb_a) == sha_a0
                ),
                "latency_ms": round(ms_arb, 3),
            })

            # ------------------------------------------------------------------
            # 4. Forbidden Scope Lock & Honest Queue Reporting (3 cases)
            # ------------------------------------------------------------------
            for forbid_path in ("core/data/secret.py", "infra/deploy.yml"):
                t0 = time.perf_counter()
                fr = sodo.tx_begin([forbid_path], prompt="forbidden", offline=True, return_dict=True)
                ms_f = (time.perf_counter() - t0) * 1000.0
                records.append({
                    "category": "scope_and_honesty",
                    "case": f"forbidden_scope:{forbid_path}",
                    "expected": "BLOCK",
                    "passed_assertion": fr.get("status") == "ERROR",
                    "latency_ms": round(ms_f, 3),
                })

            t0 = time.perf_counter()
            qr = sodo.inspect_queue_outputs(
                "clean.py",
                [{"queue_id": "Q1", "title": "Payment", "expected_outputs": ["stripe_charge", "refund_tx"], "token_cost": 300}],
            )
            ms_q = (time.perf_counter() - t0) * 1000.0
            records.append({
                "category": "scope_and_honesty",
                "case": "honest_queue_unverified_no_fake_ast",
                "expected": "UNVERIFIED",
                "passed_assertion": (
                    qr["items"][0]["status"] == "UNVERIFIED"
                    and qr["items"][0]["matched_outputs"] == []
                    and qr["captured_count"] == 0
                ),
                "latency_ms": round(ms_q, 3),
            })
        finally:
            (
                sodo.SCRIPT_DIR,
                sodo.CACHE_DIR,
                sodo.TOKEN_CACHE_FILE,
                sodo.TX_ROOT_DIR,
                sodo.ACTIVE_TX_FILE,
            ) = orig

    total = len(records)
    passed = sum(1 for r in records if r["passed_assertion"])
    failed = total - passed
    latencies = sorted(r["latency_ms"] for r in records)
    p50 = latencies[len(latencies) // 2] if latencies else 0.0
    p95 = latencies[min(len(latencies) - 1, int(len(latencies) * 0.95))] if latencies else 0.0

    cat_stats = {}
    for r in records:
        c = cat_stats.setdefault(r["category"], {"total": 0, "passed": 0})
        c["total"] += 1
        if r["passed_assertion"]:
            c["passed"] += 1

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sodonetwork_version": getattr(sodonetwork, "__version__", "unknown"),
        "environment": {
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "machine": platform.machine(),
        },
        "metrics": {
            "total_scenarios": total,
            "passed": passed,
            "failed": failed,
            "pass_rate_pct": round((passed / total * 100.0) if total else 0.0, 2),
            "latency_p50_ms": round(p50, 3),
            "latency_p95_ms": round(p95, 3),
        },
        "categories": cat_stats,
        "records": records,
    }

    json_path = os.path.join(out_dir, "tx_results.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(summary, jf, indent=2)

    md_lines = [
        f"# SodoNetwork `v{summary['sodonetwork_version']}` — Multi-File TX & Cross-Link Benchmark Report",
        "",
        f"- **Generated (UTC):** `{summary['timestamp_utc']}`",
        f"- **Environment:** `{summary['environment']['os']}` (`{summary['environment']['machine']}`) • Python `{summary['environment']['python_version']}`",
        f"- **Overall Result:** **`{passed} / {total}` (`{summary['metrics']['pass_rate_pct']}%`)** • `p50 = {p50:.3f} ms` • `p95 = {p95:.3f} ms`",
        "",
        "| Category | Passed / Total |",
        "| :--- | :---: |",
    ]
    for cat, st in cat_stats.items():
        md_lines.append(f"| `{cat}` | **{st['passed']} / {st['total']}** |")

    md_lines.extend([
        "",
        "## Case-by-Case Breakdown",
        "",
        "| Category | Case | Expected | Result | Latency (ms) |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ])
    for r in records:
        mark = "PASS" if r["passed_assertion"] else "FAIL"
        md_lines.append(f"| `{r['category']}` | `{r['case']}` | `{r['expected']}` | **{mark}** | {r['latency_ms']} |")

    md_path = os.path.join(out_dir, "TX_BENCHMARK_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write("\n".join(md_lines) + "\n")

    print(f"[TX BENCHMARK DONE] {passed}/{total} scenarios passed ({summary['metrics']['pass_rate_pct']}%) | p50={p50:.3f}ms | p95={p95:.3f}ms")
    return 0 if failed == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="SodoNetwork v4.0 TX Update Architecture Benchmark")
    parser.add_argument("--out-dir", default="results", help="Output directory for JSON and Markdown reports")
    args = parser.parse_args()
    return run_suite(args.out_dir)


if __name__ == "__main__":
    raise SystemExit(main())
