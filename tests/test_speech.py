import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins", "contextLabeler", "_vendor"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins"))
import unittest
from contextLabeler.speech import compose, TIER_VERIFIED, TIER_PARTIAL, TIER_UNVERIFIED


class TestCompose(unittest.TestCase):
    def test_verified(self):
        self.assertEqual(compose("mute", "toggle icon button", TIER_VERIFIED),
                         "toggle icon button, likely mute")

    def test_partial(self):
        self.assertEqual(compose("mute", "icon button", TIER_PARTIAL),
                         "icon button, unverified guess: mute")

    def test_unverified(self):
        self.assertEqual(compose("mute", "", TIER_UNVERIFIED),
                         "unrecognized control, possibly mute")

    def test_verified_empty_category_no_dangling_comma(self):
        result = compose("mute", "", TIER_VERIFIED)
        self.assertFalse(result.startswith(","))
        self.assertEqual(result, "likely mute")

    def test_partial_empty_category_no_dangling_comma(self):
        result = compose("mute", "", TIER_PARTIAL)
        self.assertFalse(result.startswith(","))
        self.assertEqual(result, "unverified guess: mute")

    def test_unverified_ignores_category_human(self):
        # category_human is unused in unverified tier
        r1 = compose("save", "", TIER_UNVERIFIED)
        r2 = compose("save", "whatever", TIER_UNVERIFIED)
        self.assertEqual(r1, "unrecognized control, possibly save")
        self.assertEqual(r2, "unrecognized control, possibly save")


if __name__ == "__main__":
    unittest.main()
