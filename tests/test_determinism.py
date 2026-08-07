import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins", "contextLabeler", "_vendor"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins"))
import unittest
from contextLabeler.store import LabelStore
from contextLabeler.speech import compose

FP = "deadbeef12345678"
RECORD = {
    "label": "mute",
    "category": "http://contextlabeler.org/ui-ontology#ToggleIconButton",
    "tier": "verified",
    "pinned": False,
    "created": "2026-07-05T12:00:00+00:00",
    "model": "claude-haiku-4-5-20251001",
}


def _recompose(record, human_label="toggle icon button"):
    return compose(record["label"], human_label, record["tier"])


class TestDeterminism(unittest.TestCase):
    def test_store_survives_restart(self):
        """New LabelStore instance reading the same file returns identical record."""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "labels.json")
            s1 = LabelStore(path)
            s1.store(FP, dict(RECORD))

            s2 = LabelStore(path)
            rec2 = s2.lookup(FP)
            self.assertIsNotNone(rec2)
            self.assertEqual(rec2["label"], RECORD["label"])
            self.assertEqual(rec2["category"], RECORD["category"])
            self.assertEqual(rec2["tier"], RECORD["tier"])

    def test_recomposed_utterance_is_byte_identical_across_restart(self):
        """speech.compose from the persisted record is byte-identical on every call."""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "labels.json")
            s1 = LabelStore(path)
            s1.store(FP, dict(RECORD))
            u1 = _recompose(s1.lookup(FP))

            s2 = LabelStore(path)
            u2 = _recompose(s2.lookup(FP))

            s3 = LabelStore(path)
            u3 = _recompose(s3.lookup(FP))

            self.assertEqual(u1, u2)
            self.assertEqual(u2, u3)
            self.assertEqual(u1, "toggle icon button, likely mute")

    def test_nondeterministic_classifier_cannot_change_stored_label(self):
        """Once a record is stored, a subsequent store() call with a different answer
        on the same fp is never reached when the lookup path is used correctly."""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "labels.json")
            s = LabelStore(path)
            s.store(FP, dict(RECORD))

            # Simulate what the plugin does: lookup first, only classify on miss
            def resolve(fp, classifier_answer):
                record = s.lookup(fp)
                if record:
                    return _recompose(record)
                # Miss — would call classifier and store
                s.store(fp, classifier_answer)
                return _recompose(classifier_answer)

            different_record = {**RECORD, "label": "unmute", "tier": "partial"}
            u1 = resolve(FP, different_record)
            u2 = resolve(FP, different_record)
            u3 = resolve(FP, different_record)

            # All calls return the original stored value, not the "different" classifier answer
            self.assertEqual(u1, u2)
            self.assertEqual(u2, u3)
            self.assertIn("mute", u1)
            self.assertNotIn("unmute", u1)

    def test_pinned_label_not_overwritten_by_relabel(self):
        """Pinned records survive a delete attempt (simulating pin check in relabel)."""
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "labels.json")
            s = LabelStore(path)
            s.store(FP, dict(RECORD))
            s.pin(FP)

            # Simulate script_relabelFocused: check pinned before deleting
            record = s.lookup(FP)
            if not record or not record.get("pinned", False):
                s.delete(FP)

            self.assertIsNotNone(s.lookup(FP))
            self.assertTrue(s.lookup(FP)["pinned"])


if __name__ == "__main__":
    unittest.main()
