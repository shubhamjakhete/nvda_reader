import sys, os, tempfile, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins", "contextLabeler", "_vendor"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins"))
import unittest
from contextLabeler.store import LabelStore, MAX_RECORDS

SAMPLE = {
    "label": "mute",
    "category": "http://contextlabeler.org/ui-ontology#ToggleIconButton",
    "tier": "verified",
    "pinned": False,
    "created": "2026-07-05T12:00:00+00:00",
    "model": "claude-haiku-4-5-20251001",
}


class TestLabelStore(unittest.TestCase):
    def _store(self, d):
        return LabelStore(os.path.join(d, "labels.json"))

    def test_round_trip_save_load(self):
        with tempfile.TemporaryDirectory() as d:
            s = self._store(d)
            s.store("fp1", dict(SAMPLE))
            s2 = LabelStore(s._path)
            rec = s2.lookup("fp1")
            self.assertIsNotNone(rec)
            self.assertEqual(rec["label"], "mute")
            self.assertEqual(rec["tier"], "verified")

    def test_lookup_missing_returns_none(self):
        with tempfile.TemporaryDirectory() as d:
            s = self._store(d)
            self.assertIsNone(s.lookup("nonexistent"))

    def test_corrupt_file_falls_back_to_empty(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "labels.json")
            with open(path, "w") as f:
                f.write("not valid json {{{{")
            s = LabelStore(path)
            self.assertIsNone(s.lookup("anything"))

    def test_missing_file_falls_back_to_empty(self):
        with tempfile.TemporaryDirectory() as d:
            s = LabelStore(os.path.join(d, "nonexistent.json"))
            self.assertIsNone(s.lookup("fp1"))

    def test_pin(self):
        with tempfile.TemporaryDirectory() as d:
            s = self._store(d)
            s.store("fp1", dict(SAMPLE))
            s.pin("fp1")
            s2 = LabelStore(s._path)
            self.assertTrue(s2.lookup("fp1")["pinned"])

    def test_delete(self):
        with tempfile.TemporaryDirectory() as d:
            s = self._store(d)
            s.store("fp1", dict(SAMPLE))
            s.delete("fp1")
            self.assertIsNone(s.lookup("fp1"))

    def test_atomic_write_no_tmp_on_success(self):
        with tempfile.TemporaryDirectory() as d:
            s = self._store(d)
            s.store("fp1", dict(SAMPLE))
            # After a successful write, the .tmp file must not exist
            self.assertFalse(os.path.exists(s._path + ".tmp"))
            self.assertTrue(os.path.exists(s._path))

    def test_eviction_removes_oldest_unpinned(self):
        with tempfile.TemporaryDirectory() as d:
            s = self._store(d)
            # Fill to MAX_RECORDS with unpinned entries
            for i in range(MAX_RECORDS):
                s._data[f"key{i}"] = {**SAMPLE, "pinned": False}
            # One more store call should evict key0 (oldest)
            s.store("new_key", dict(SAMPLE))
            self.assertIsNone(s.lookup("key0"))
            self.assertIsNotNone(s.lookup("new_key"))

    def test_eviction_never_removes_pinned(self):
        with tempfile.TemporaryDirectory() as d:
            s = self._store(d)
            # Insert a pinned entry first (oldest position)
            s._data["pinned_key"] = {**SAMPLE, "pinned": True}
            # Fill remaining slots with unpinned
            for i in range(MAX_RECORDS - 1):
                s._data[f"key{i}"] = {**SAMPLE, "pinned": False}
            # Adding one more should evict an unpinned entry, not pinned_key
            s.store("overflow_key", dict(SAMPLE))
            self.assertIsNotNone(s.lookup("pinned_key"))


if __name__ == "__main__":
    unittest.main()
