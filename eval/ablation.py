#!/usr/bin/env python3
"""
Ablation study: Condition A (ontology-constrained) vs Condition B (free-form).

usage: python3 eval/ablation.py <api-key>
       [--benchmark eval/benchmark.json]
       [--limit N]
"""
import argparse
import importlib.util
import json
import os
import sys

_dir = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("replay", os.path.join(_dir, "replay.py"))
_replay_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_replay_mod)
run_replay = _replay_mod.run_replay


def _tag_stats(metrics, tag):
    return metrics.get("per_tag", {}).get(tag, {})


def run_ablation(api_key, benchmark_path, limit):
    print("\n" + "=" * 60)
    print("CONDITION A — Constrained (ontology-grounded)")
    print("=" * 60)
    a = run_replay(api_key, benchmark_path, "constrained", 1, limit, "eval/ablation_a.json")

    print("\n" + "=" * 60)
    print("CONDITION B — Free-form (no ontology constraint)")
    print("=" * 60)
    b = run_replay(api_key, benchmark_path, "freeform", 1, limit, "eval/ablation_b.json")

    am, bm = a["metrics"], b["metrics"]

    # % of B's results that the ontology filter would have caught
    b_valid = [r for r in b["results"] if "error" not in r]
    b_invalid = [r for r in b_valid if not r.get("is_valid_leaf", True)]
    pct_caught = len(b_invalid) / len(b_valid) if b_valid else 0

    print("\n" + "=" * 60)
    print("ABLATION TABLE")
    print("=" * 60)
    hdr = f"{'Condition':<26} {'CatAcc':>7} {'LblAcc':>7} {'Invalid%':>9} {'Fallback%':>10}"
    print(hdr)
    print("-" * 60)
    print(f"{'A (constrained)':<26} {am['category_accuracy']:>7.3f} {am['label_accuracy']:>7.3f}"
          f" {am['invalid_category_rate']:>9.3f} {am['fallback_recovery_rate']:>10.3f}")
    print(f"{'B (free-form)':<26} {bm['category_accuracy']:>7.3f} {bm['label_accuracy']:>7.3f}"
          f" {bm['invalid_category_rate']:>9.3f} {'N/A':>10}")
    print(f"\n  Free-form invalid outputs ontology would catch: {pct_caught:.1%}")

    print("\n--- Adversarial tag ---")
    a_adv = _tag_stats(am, "adversarial")
    b_adv = _tag_stats(bm, "adversarial")
    if a_adv:
        print(f"  A: n={a_adv['n']} cat={a_adv['category_accuracy']:.2f}"
              f" lbl={a_adv['label_accuracy']:.2f} invalid={a_adv['invalid_rate']:.2f}")
    if b_adv:
        print(f"  B: n={b_adv['n']} cat={b_adv['category_accuracy']:.2f}"
              f" lbl={b_adv['label_accuracy']:.2f} invalid={b_adv['invalid_rate']:.2f}")

    report = {
        "condition_a": am,
        "condition_b": bm,
        "freeform_pct_caught_by_ontology": round(pct_caught, 3),
    }
    out = "eval/ablation_results.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nAblation report written to {out}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ContextLabeler ablation study")
    parser.add_argument("api_key", help="Anthropic API key")
    parser.add_argument("--benchmark", default="eval/benchmark.json")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    run_ablation(args.api_key, args.benchmark, args.limit)
