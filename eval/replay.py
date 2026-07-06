#!/usr/bin/env python3
"""
Benchmark replay harness.

usage: python3 eval/replay.py <api-key>
       [--benchmark eval/benchmark.json]
       [--mode constrained|freeform]
       [--runs 1]
       [--limit N]
       [--out eval/results.json]
"""
import argparse
import json
import os
import sys
import time

# Ensure vendored libs and plugin package are importable
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_root, "globalPlugins", "contextLabeler", "_vendor"))
sys.path.insert(0, os.path.join(_root, "globalPlugins"))

from contextLabeler.ontology import Ontology
from contextLabeler import classifier

NS = "http://contextlabeler.org/ui-ontology#"


def expand(uri: str) -> str:
    if uri.startswith(":"):
        return NS + uri[1:]
    return uri


def run_replay(api_key, benchmark_path, mode, runs, limit, out_path):
    ont = Ontology.load_default()

    with open(benchmark_path, encoding="utf-8") as f:
        entries = json.load(f)

    if limit:
        entries = entries[:limit]

    results = []

    total = len(entries) * runs
    done = 0

    for entry in entries:
        for run_n in range(runs):
            t0 = time.time()
            try:
                if mode == "freeform":
                    result = classifier.classify(entry["ctx"], [], api_key, freeform=True)
                else:
                    allowed = ont.leaf_uris()
                    descs = ont.leaf_descriptions()
                    result = classifier.classify(entry["ctx"], allowed, api_key, descs)

                latency = time.time() - t0
                raw_cat = result["category"]
                expanded = expand(raw_cat)
                is_valid = ont.is_valid_leaf(expanded)
                ancestor = ont.nearest_valid_ancestor(expanded) if not is_valid else None

                expected_exp = expand(entry["expected_category"])
                cat_correct = expanded == expected_exp
                label_correct = result["label"].lower().strip() in [
                    lbl.lower().strip() for lbl in entry.get("acceptable_labels", [])
                ]

                results.append({
                    "id": entry["id"],
                    "run": run_n,
                    "tags": entry.get("tags", []),
                    "expected_category": expected_exp,
                    "raw_category": raw_cat,
                    "expanded_category": expanded,
                    "label": result["label"],
                    "is_valid_leaf": is_valid,
                    "ancestor_fallback": ancestor,
                    "category_correct": cat_correct,
                    "label_correct": label_correct,
                    "latency": round(latency, 3),
                })
            except Exception as e:
                results.append({
                    "id": entry["id"],
                    "run": run_n,
                    "tags": entry.get("tags", []),
                    "error": str(e),
                    "category_correct": False,
                    "label_correct": False,
                    "latency": round(time.time() - t0, 3),
                })

            done += 1
            print(f"  [{done}/{total}] {entry['id']} run={run_n}", flush=True)
            time.sleep(0.5)

    valid = [r for r in results if "error" not in r]
    n = len(valid)

    cat_acc = sum(r["category_correct"] for r in valid) / n if n else 0
    label_acc = sum(r["label_correct"] for r in valid) / n if n else 0
    invalid_rate = sum(not r["is_valid_leaf"] for r in valid) / n if n else 0

    invalid_set = [r for r in valid if not r["is_valid_leaf"]]
    fallback_rate = (
        sum(r["ancestor_fallback"] is not None for r in invalid_set) / len(invalid_set)
        if invalid_set else 0
    )

    lats = sorted(r["latency"] for r in results)
    p50 = lats[len(lats) // 2] if lats else 0
    p95 = lats[max(0, int(len(lats) * 0.95) - 1)] if lats else 0

    # Per-tag breakdown
    all_tags = sorted({t for r in results for t in r.get("tags", [])})
    per_tag = {}
    for tag in all_tags:
        tagged = [r for r in valid if tag in r.get("tags", [])]
        if not tagged:
            continue
        per_tag[tag] = {
            "n": len(tagged),
            "category_accuracy": round(sum(r["category_correct"] for r in tagged) / len(tagged), 3),
            "label_accuracy": round(sum(r["label_correct"] for r in tagged) / len(tagged), 3),
            "invalid_rate": round(sum(not r["is_valid_leaf"] for r in tagged) / len(tagged), 3),
        }

    metrics = {
        "mode": mode,
        "n_entries": len(entries),
        "n_runs": runs,
        "n_results": len(results),
        "errors": len(results) - n,
        "category_accuracy": round(cat_acc, 3),
        "label_accuracy": round(label_acc, 3),
        "invalid_category_rate": round(invalid_rate, 3),
        "fallback_recovery_rate": round(fallback_rate, 3),
        "latency_p50_s": round(p50, 3),
        "latency_p95_s": round(p95, 3),
        "per_tag": per_tag,
    }

    print("\n=== Replay Results ===")
    for k, v in metrics.items():
        if k != "per_tag":
            print(f"  {k}: {v}")
    print("\nPer-tag breakdown:")
    for tag, stats in per_tag.items():
        print(f"  [{tag}] n={stats['n']} cat={stats['category_accuracy']:.2f}"
              f" lbl={stats['label_accuracy']:.2f} invalid={stats['invalid_rate']:.2f}")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    output = {"metrics": metrics, "results": results}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults written to {out_path}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ContextLabeler benchmark replay harness")
    parser.add_argument("api_key", help="Anthropic API key")
    parser.add_argument("--benchmark", default="eval/benchmark.json")
    parser.add_argument("--mode", choices=["constrained", "freeform"], default="constrained")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--limit", type=int, default=None, help="Limit to first N entries")
    parser.add_argument("--out", default="eval/results.json")
    args = parser.parse_args()

    run_replay(args.api_key, args.benchmark, args.mode, args.runs, args.limit, args.out)
