#!/usr/bin/env python3
"""
Layer-1 consistency test: run each benchmark entry RUNS_PER_ENTRY times and
measure raw LLM variance in category and label output.

Layer-2 determinism (store-level) is covered by tests/test_determinism.py.

usage: python3 eval/consistency.py <api-key>
       [--benchmark eval/benchmark.json]
       [--runs 10]
       [--limit N]
       [--out eval/consistency_results.json]
"""
import argparse
import json
import os
import sys
import time

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


def run_consistency(api_key, benchmark_path, runs_per_entry, limit, out_path):
    ont = Ontology.load_default()

    with open(benchmark_path, encoding="utf-8") as f:
        entries = json.load(f)

    if limit:
        entries = entries[:limit]

    allowed = ont.leaf_uris()
    descs = ont.leaf_descriptions()

    per_entry = {}
    total = len(entries) * runs_per_entry
    done = 0

    for entry in entries:
        categories = []
        labels = []
        valid_flags = []

        for _ in range(runs_per_entry):
            try:
                result = classifier.classify(entry["ctx"], allowed, api_key, descs)
                cat = expand(result["category"])
                categories.append(cat)
                labels.append(result["label"].lower().strip())
                valid_flags.append(ont.is_valid_leaf(cat))
            except Exception as e:
                categories.append("ERROR")
                labels.append("ERROR")
                valid_flags.append(False)

            done += 1
            print(f"  [{done}/{total}] {entry['id']}", flush=True)
            time.sleep(0.5)

        modal_cat = max(set(categories), key=categories.count) if categories else ""
        cat_agree = categories.count(modal_cat) / len(categories) if categories else 0
        distinct_labels = len(set(labels))
        validity_flips = sum(
            1 for i in range(1, len(valid_flags)) if valid_flags[i] != valid_flags[i - 1]
        )

        per_entry[entry["id"]] = {
            "tags": entry.get("tags", []),
            "categories": categories,
            "labels": labels,
            "modal_category": modal_cat,
            "category_agreement_rate": round(cat_agree, 3),
            "distinct_labels": distinct_labels,
            "has_validity_flip": validity_flips > 0,
        }

    entries_data = list(per_entry.values())
    avg_agree = sum(e["category_agreement_rate"] for e in entries_data) / len(entries_data) if entries_data else 0
    avg_distinct = sum(e["distinct_labels"] for e in entries_data) / len(entries_data) if entries_data else 0
    pct_flip = sum(e["has_validity_flip"] for e in entries_data) / len(entries_data) if entries_data else 0

    metrics = {
        "n_entries": len(entries),
        "runs_per_entry": runs_per_entry,
        "avg_category_agreement_rate": round(avg_agree, 3),
        "avg_distinct_labels_per_entry": round(avg_distinct, 2),
        "pct_entries_with_validity_flip": round(pct_flip, 3),
    }

    print("\n=== Consistency Results (Layer 1 — LLM variance) ===")
    print(f"  Entries tested:                {metrics['n_entries']}")
    print(f"  Runs per entry:                {metrics['runs_per_entry']}")
    print(f"  Avg category agreement rate:   {metrics['avg_category_agreement_rate']:.1%}")
    print(f"  Avg distinct labels/entry:     {metrics['avg_distinct_labels_per_entry']:.1f}")
    print(f"  % entries with valid/inv flip: {metrics['pct_entries_with_validity_flip']:.1%}")
    print("\n  (Layer 2 — store determinism is proven by tests/test_determinism.py)")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    output = {"metrics": metrics, "per_entry": per_entry}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults written to {out_path}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ContextLabeler LLM consistency measurement")
    parser.add_argument("api_key", help="Anthropic API key")
    parser.add_argument("--benchmark", default="eval/benchmark.json")
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", default="eval/consistency_results.json")
    args = parser.parse_args()

    run_consistency(args.api_key, args.benchmark, args.runs, args.limit, args.out)
