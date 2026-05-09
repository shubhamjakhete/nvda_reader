#!/usr/bin/env python3
"""
One-shot smoke test: hits api.anthropic.com with a sample UI element context.
Usage: python3 scripts/smoke-test-api.py <your-api-key>
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins", "contextLabeler", "_vendor"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins"))

from contextLabeler.ontology import Ontology
from contextLabeler.classifier import classify

if len(sys.argv) < 2:
    print("Usage: python3 scripts/smoke-test-api.py <api-key>")
    sys.exit(1)

api_key = sys.argv[1]

ont = Ontology.load_default()
allowed_uris = ont.leaf_uris()

# Simulate what the add-on would see on an unlabeled save button in Discord
ctx = {
    "role": "button",
    "name": "",
    "description": "",
    "window_class": "Chrome_WidgetWin_1",
    "window_text": "",
    "app_name": "discord",
    "parent_role": "toolbar",
    "parent_name": "Message actions",
    "sibling_names": ["Reply", "React", "More"],
    "window_title": "Discord",
}

print("Allowed leaf URIs:", len(allowed_uris))
print("Sending classification request to Claude...")

result = classify(ctx, allowed_uris, api_key)
print("\nRaw result:", result)

category = result.get("category", "")
label = result.get("label", "")
valid = ont.is_valid_leaf(category)
human = ont.label_for(category) if valid else "INVALID"

print(f"\ncategory : {category}")
print(f"label    : {label}")
print(f"valid    : {valid}")
print(f"human    : {human}")
if valid:
    speakable = f"{label} — {human}"
    print(f"\nNVDA would speak: \"{speakable}\"")
    print("\nSMOKE TEST PASSED")
else:
    print("\nSMOKE TEST FAILED — invalid category returned")
