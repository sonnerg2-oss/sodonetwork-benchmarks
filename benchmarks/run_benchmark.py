#!/usr/bin/env python3
"""
SodoNetwork Independent & Reproducible Code Mutation Guard Benchmark
====================================================================
Tests the REAL PyPI package `sodonetwork` against real Python Standard Library
source files (independent third-party corpus present on every Python runtime
and GitHub Actions runner).

Design Principles (Zero Self-Benchmarking Bias):
  1. Every generated defect mutation is AST-verified (`ast.parse`) so it remains
     100% syntactically valid Python — ensuring `py_compile` is tested fairly on
     defects that static syntax compilers CANNOT see.
  2. Separates:
     - Benign edits (clean helper append, moderate <20% valid AST trim, normal comments)
     - Non-shrinking lazy LLM placeholders (tests phrase detector WITHOUT triggering >35% byte shrink)
     - Shrinking destructive deletions (AST node removal >50% without placeholder comments)
     - Empty / whitespace wipes

Outputs raw JSON, CSV, and transparent Markdown summary to `results/`.
"""

import argparse
import ast
import csv
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import sodonetwork
from sodonetwork.cli import capture_preflight_snapshot, verify_code_mutation_integrity


CORPUS_MODULES = [
    "json/encoder.py",
    "json/decoder.py",
    "http/client.py",
    "http/server.py",
    "urllib/parse.py",
    "urllib/request.py",
    "email/message.py",
    "email/parser.py",
    "argparse.py",
    "pathlib.py",
    "logging/__init__.py",
    "subprocess.py",
    "shutil.py",
    "ast.py",
    "unittest/case.py",
    "csv.py",
    "configparser.py",
    "difflib.py",
    "inspect.py",
    "sqlite3/dbapi2.py",
]

# Tested WITHOUT triggering >35% size shrink so we genuinely measure phrase detection recall & gaps.
LAZY_PHRASE_VARIANTS = [
    ("known_rest_of_code", "# ... rest of code unchanged ..."),
    ("known_existing_code", "# existing code here"),
    ("known_remaining_unchanged", "# remaining code unchanged"),
    ("known_impl_unchanged", "# existing implementation unchanged"),
    ("variant_omitted_brevity", "# ... omitted for brevity ..."),
    ("variant_methods_unchanged", "# ... other helper methods remain unchanged ..."),
    ("variant_inline_comment", "x_placeholder = True  # rest of code unchanged"),
]


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = (len(ordered) - 1) * (pct / 100.0)
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return ordered[int(idx)]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (idx - lo)


def run_py_compile(filepath: str) -> Tuple[bool, float]:
    t0 = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "py_compile", filepath],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
        timeout=15,
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    return (proc.returncode == 0), elapsed_ms


def run_sodo_guard(filepath: str, preflight: Dict[str, Any]) -> Tuple[bool, str, float]:
    t0 = time.perf_counter()
    res = verify_code_mutation_integrity(filepath, preflight)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    passed = bool(res.get("passed"))
    detail = str(res.get("error") or res.get("details") or "")
    return passed, detail, elapsed_ms


def discover_corpus() -> List[Tuple[str, str]]:
    stdlib_dir = sysconfig.get_paths()["stdlib"]
    found: List[Tuple[str, str]] = []
    for rel in CORPUS_MODULES:
        full = os.path.join(stdlib_dir, rel.replace("/", os.sep))
        if os.path.isfile(full):
            found.append((rel, full))
    return found


def make_ast_safe_prefix(src: str, target_ratio: float) -> str:
    """
    Truncates top-level AST nodes to approximately `target_ratio` of original lines
    while guaranteeing 100% syntactically valid Python output (`ast.parse`).
    """
    tree = ast.parse(src)
    lines = src.splitlines()
    cutoff_line = max(5, int(len(lines) * target_ratio))
    kept_nodes = []
    for node in tree.body:
        end_ln = getattr(node, "end_lineno", None)
        if end_ln and end_ln <= cutoff_line:
            kept_nodes.append(node)
        elif not kept_nodes:
            kept_nodes.append(node)
            break
        else:
            break

    while kept_nodes:
        end_ln = getattr(kept_nodes[-1], "end_lineno", len(lines))
        candidate = "\n".join(lines[:end_ln])
        try:
            ast.parse(candidate)
            return candidate
        except SyntaxError:
            kept_nodes.pop()
    return "pass\n"


def pad_to_avoid_shrink(prefix: str, orig_bytes: int, comment_line: str) -> str:
    """
    Creates a valid Python function containing `comment_line` and benign filler statements
    so byte size stays >= 75% of original — isolating lazy-phrase detection from shrink-size detection.
    """
    header = (
        f"{prefix}\n\n"
        "def _llm_truncated_stub(item_id: int = 0) -> int:\n"
        f"    {comment_line}\n"
        "    return item_id\n\n"
    )
    filler_line = "_BENCHMARK_NOOP_STATE = 0\n"
    cur_bytes = len(header.encode("utf-8"))
    target_bytes = int(orig_bytes * 0.78)
    if cur_bytes < target_bytes:
        needed = ((target_bytes - cur_bytes) // len(filler_line)) + 2
        header += filler_line * needed
    ast.parse(header)
    return header


def make_benign_refactor(src: str) -> str:
    addition = (
        "\n\ndef _sodo_benchmark_helper(value: str) -> str:\n"
        "    \"\"\"Benign valid helper appended for clean mutation benchmark.\"\"\"\n"
        "    # Standard refactor note without omission placeholders.\n"
        "    return value.strip()\n"
    )
    out = src + addition
    ast.parse(out)
    return out


def make_moderate_clean_trim(src: str) -> str:
    """Removes ~15-25% trailing top-level nodes cleanly (within allowed <35% shrink)."""
    trimmed = make_ast_safe_prefix(src, 0.80)
    # Only keep as moderate trim if it genuinely stays >= 68% of original bytes
    orig_bytes = len(src.encode("utf-8"))
    if len(trimmed.encode("utf-8")) < int(orig_bytes * 0.68):
        return make_benign_refactor(src)
    return trimmed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run reproducible SodoNetwork benchmark on Python stdlib.")
    parser.add_argument("--out-dir", default=os.path.join(os.path.dirname(os.path.dirname(__file__)), "results"))
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    corpus = discover_corpus()
    if not corpus:
        print("ERROR: No stdlib corpus files found.", file=sys.stderr)
        return 1

    cases: List[Dict[str, Any]] = []
    tmpdir = tempfile.mkdtemp(prefix="sodo_bench_")
    try:
        for mod_rel, mod_path in corpus:
            with open(mod_path, "r", encoding="utf-8", errors="ignore") as f:
                orig_src = f.read()

            work_file = os.path.join(tmpdir, mod_rel.replace("/", "_"))
            with open(work_file, "w", encoding="utf-8") as wf:
                wf.write(orig_src)
            preflight = capture_preflight_snapshot(work_file)
            orig_bytes = len(orig_src.encode("utf-8"))

            # 1. Negative Case A: Clean Benign Helper Append (Expected: ALLOW)
            benign_src = make_benign_refactor(orig_src)
            with open(work_file, "w", encoding="utf-8") as wf:
                wf.write(benign_src)
            py_ok, py_ms = run_py_compile(work_file)
            sodo_ok, sodo_detail, sodo_ms = run_sodo_guard(work_file, preflight)
            cases.append({
                "module": mod_rel,
                "orig_bytes": orig_bytes,
                "category": "benign_clean_edit",
                "variant": "append_helper",
                "expected_block": False,
                "py_compile_passed": py_ok,
                "py_compile_ms": round(py_ms, 3),
                "sodo_blocked": not sodo_ok,
                "sodo_guard_ms": round(sodo_ms, 3),
                "sodo_detail": sodo_detail,
            })

            # 2. Negative Case B: Moderate Clean Refactor (~20% trim, below 35% threshold -> Expected: ALLOW)
            mod_src = make_moderate_clean_trim(orig_src)
            with open(work_file, "w", encoding="utf-8") as wf:
                wf.write(mod_src)
            py_ok, py_ms = run_py_compile(work_file)
            sodo_ok, sodo_detail, sodo_ms = run_sodo_guard(work_file, preflight)
            cases.append({
                "module": mod_rel,
                "orig_bytes": orig_bytes,
                "category": "benign_clean_edit",
                "variant": "moderate_valid_trim_under_35pct",
                "expected_block": False,
                "py_compile_passed": py_ok,
                "py_compile_ms": round(py_ms, 3),
                "sodo_blocked": not sodo_ok,
                "sodo_guard_ms": round(sodo_ms, 3),
                "sodo_detail": sodo_detail,
            })

            # 3. Positive Case A: Non-Shrinking Lazy Truncation Variants (Expected: BLOCK)
            safe_head = make_ast_safe_prefix(orig_src, 0.25)
            for v_name, comment in LAZY_PHRASE_VARIANTS:
                mut_src = pad_to_avoid_shrink(safe_head, orig_bytes, comment)
                with open(work_file, "w", encoding="utf-8") as wf:
                    wf.write(mut_src)
                py_ok, py_ms = run_py_compile(work_file)
                sodo_ok, sodo_detail, sodo_ms = run_sodo_guard(work_file, preflight)
                cases.append({
                    "module": mod_rel,
                    "orig_bytes": orig_bytes,
                    "category": "lazy_truncation_no_shrink",
                    "variant": v_name,
                    "expected_block": True,
                    "py_compile_passed": py_ok,
                    "py_compile_ms": round(py_ms, 3),
                    "sodo_blocked": not sodo_ok,
                    "sodo_guard_ms": round(sodo_ms, 3),
                    "sodo_detail": sodo_detail,
                })

            # 4. Positive Case B: AST-Valid Destructive Shrink (>50% code removed, no comment -> Expected: BLOCK)
            shrink_src = make_ast_safe_prefix(orig_src, 0.15)
            if len(shrink_src.encode("utf-8")) >= int(orig_bytes * 0.65):
                # Force AST-valid minimal header if first node is huge
                shrink_src = "_MINIMAL_STUB = True\n"
            with open(work_file, "w", encoding="utf-8") as wf:
                wf.write(shrink_src)
            py_ok, py_ms = run_py_compile(work_file)
            sodo_ok, sodo_detail, sodo_ms = run_sodo_guard(work_file, preflight)
            cases.append({
                "module": mod_rel,
                "orig_bytes": orig_bytes,
                "category": "destructive_shrink",
                "variant": "ast_valid_mass_delete",
                "expected_block": True,
                "py_compile_passed": py_ok,
                "py_compile_ms": round(py_ms, 3),
                "sodo_blocked": not sodo_ok,
                "sodo_guard_ms": round(sodo_ms, 3),
                "sodo_detail": sodo_detail,
            })

            # 5. Positive Case C: Empty / Whitespace Wipe (Expected: BLOCK)
            with open(work_file, "w", encoding="utf-8") as wf:
                wf.write("   \n")
            py_ok, py_ms = run_py_compile(work_file)
            sodo_ok, sodo_detail, sodo_ms = run_sodo_guard(work_file, preflight)
            cases.append({
                "module": mod_rel,
                "orig_bytes": orig_bytes,
                "category": "empty_wipe",
                "variant": "whitespace_only",
                "expected_block": True,
                "py_compile_passed": py_ok,
                "py_compile_ms": round(py_ms, 3),
                "sodo_blocked": not sodo_ok,
                "sodo_guard_ms": round(sodo_ms, 3),
                "sodo_detail": sodo_detail,
            })
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    pos_cases = [c for c in cases if c["expected_block"]]
    neg_cases = [c for c in cases if not c["expected_block"]]

    tp = sum(1 for c in pos_cases if c["sodo_blocked"])
    fn = sum(1 for c in pos_cases if not c["sodo_blocked"])
    fp = sum(1 for c in neg_cases if c["sodo_blocked"])
    tn = sum(1 for c in neg_cases if not c["sodo_blocked"])

    baseline_silent_pass = sum(1 for c in pos_cases if c["py_compile_passed"])
    baseline_caught = len(pos_cases) - baseline_silent_pass

    recall = (tp / len(pos_cases) * 100.0) if pos_cases else 0.0
    fpr = (fp / len(neg_cases) * 100.0) if neg_cases else 0.0
    precision = (tp / (tp + fp) * 100.0) if (tp + fp) else 0.0

    sodo_latencies = [c["sodo_guard_ms"] for c in cases]
    py_latencies = [c["py_compile_ms"] for c in cases]

    variant_stats: Dict[str, Dict[str, int]] = {}
    for c in cases:
        key = f"{c['category']}::{c['variant']}"
        bucket = variant_stats.setdefault(key, {"total": 0, "sodo_blocked": 0, "py_compile_passed": 0})
        bucket["total"] += 1
        if c["sodo_blocked"]:
            bucket["sodo_blocked"] += 1
        if c["py_compile_passed"]:
            bucket["py_compile_passed"] += 1

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sodonetwork_version": getattr(sodonetwork, "__version__", "unknown"),
        "environment": {
            "python_version": platform.python_version(),
            "os": f"{platform.system()} {platform.release()}",
            "machine": platform.machine(),
            "corpus_modules_count": len(corpus),
        },
        "totals": {
            "total_cases": len(cases),
            "positive_defect_cases": len(pos_cases),
            "negative_benign_cases": len(neg_cases),
        },
        "control_baseline_py_compile": {
            "defects_silently_passed": baseline_silent_pass,
            "defects_caught": baseline_caught,
            "silent_pass_rate_pct": round((baseline_silent_pass / len(pos_cases) * 100.0) if pos_cases else 0.0, 2),
            "latency_p50_ms": round(percentile(py_latencies, 50), 3),
            "latency_p95_ms": round(percentile(py_latencies, 95), 3),
        },
        "sodonetwork_guard": {
            "true_positive": tp,
            "false_negative": fn,
            "false_positive": fp,
            "true_negative": tn,
            "recall_pct": round(recall, 2),
            "precision_pct": round(precision, 2),
            "false_positive_rate_pct": round(fpr, 2),
            "latency_p50_ms": round(percentile(sodo_latencies, 50), 3),
            "latency_p95_ms": round(percentile(sodo_latencies, 95), 3),
            "latency_p99_ms": round(percentile(sodo_latencies, 99), 3),
        },
        "variant_breakdown": variant_stats,
    }

    json_path = os.path.join(args.out_dir, "latest_results.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(summary, jf, indent=2)

    csv_path = os.path.join(args.out_dir, "latest_cases.csv")
    fieldnames = list(cases[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cases)

    md_lines = [
        "# SodoNetwork Independent Benchmark Report",
        "",
        f"- **Timestamp (UTC):** `{summary['timestamp_utc']}`",
        f"- **Package Version:** `sodonetwork=={summary['sodonetwork_version']}`",
        f"- **Environment:** Python `{summary['environment']['python_version']}` on `{summary['environment']['os']}` (`{summary['environment']['machine']}`)",
        f"- **Independent Corpus:** `{len(corpus)}` real Python Standard Library files (`total {len(cases)} AST-valid mutated test cases`)",
        "",
        "## Control (`py_compile` alone) vs. `sodonetwork` Mutation Guard",
        "",
        "| Metric | Control (`py_compile` alone) | SodoNetwork Guard (`verify_code_mutation_integrity`) |",
        "| :--- | :---: | :---: |",
        f"| Defect Cases Evaluated (All AST-Valid) | {len(pos_cases)} | {len(pos_cases)} |",
        f"| Defects Silently Passed | **{baseline_silent_pass}** ({summary['control_baseline_py_compile']['silent_pass_rate_pct']}%) | **{fn}** (False Negatives) |",
        f"| Defects Blocked (Recall / TPR) | {baseline_caught} | **{tp}/{len(pos_cases)} ({summary['sodonetwork_guard']['recall_pct']}%)** |",
        f"| Benign Clean Edits (False Positives) | — | **{fp}/{len(neg_cases)} ({summary['sodonetwork_guard']['false_positive_rate_pct']}% FPR)** |",
        f"| Precision | — | **{summary['sodonetwork_guard']['precision_pct']}%** |",
        f"| Latency p50 | {summary['control_baseline_py_compile']['latency_p50_ms']} ms | **{summary['sodonetwork_guard']['latency_p50_ms']} ms** |",
        f"| Latency p95 | {summary['control_baseline_py_compile']['latency_p95_ms']} ms | **{summary['sodonetwork_guard']['latency_p95_ms']} ms** |",
        "",
        "## Per-Variant Breakdown (Including Real Detection Gaps)",
        "",
        "| Category :: Variant | Cases | `py_compile` Passed Silently | SodoNetwork Blocked |",
        "| :--- | :---: | :---: | :---: |",
    ]
    for k, st in variant_stats.items():
        md_lines.append(f"| `{k}` | {st['total']} | {st['py_compile_passed']}/{st['total']} | {st['sodo_blocked']}/{st['total']} |")

    md_lines.extend([
        "",
        "## Reproducibility",
        "```bash",
        "pip install sodonetwork==3.6.1",
        "python benchmarks/run_benchmark.py",
        "```",
    ])
    md_path = os.path.join(args.out_dir, "BENCHMARK_REPORT.md")
    with open(md_path, "w", encoding="utf-8") as mf:
        mf.write("\n".join(md_lines) + "\n")

    print(f"[BENCHMARK DONE] {len(cases)} AST-valid cases across {len(corpus)} stdlib modules.")
    print(f"Control (py_compile) silently passed defects: {baseline_silent_pass}/{len(pos_cases)}")
    print(f"SodoNetwork Guard: TP={tp}, FN={fn}, FP={fp}, TN={tn} | Recall={summary['sodonetwork_guard']['recall_pct']}% | FPR={summary['sodonetwork_guard']['false_positive_rate_pct']}% | p95={summary['sodonetwork_guard']['latency_p95_ms']} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
