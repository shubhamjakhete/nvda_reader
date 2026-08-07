import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins", "contextLabeler", "_vendor"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins"))
import unittest
from contextLabeler.cache import fingerprint

BASE = {
    "app_name": "discord",
    "window_class": "Chrome_WidgetWin_1",
    "role": "button",
    "html_class": "btn-mute",
    "parent_role": "toolbar",
    "parent_name": "Message actions",
    "position_in_parent": 2,
    "name": "",
    "automation_id": "",
    "window_title": "Discord — #general",
    "window_text": "Discord",
}


class TestFingerprint(unittest.TestCase):
    def test_ignores_window_title(self):
        ctx1 = {**BASE, "window_title": "Discord — #general"}
        ctx2 = {**BASE, "window_title": "Discord — #random"}
        self.assertEqual(fingerprint(ctx1), fingerprint(ctx2))

    def test_ignores_window_text(self):
        ctx1 = {**BASE, "window_text": "3 unread"}
        ctx2 = {**BASE, "window_text": "no messages"}
        self.assertEqual(fingerprint(ctx1), fingerprint(ctx2))

    def test_differs_on_automation_id(self):
        ctx1 = {**BASE, "automation_id": "btn-mute-1"}
        ctx2 = {**BASE, "automation_id": "btn-mute-2"}
        self.assertNotEqual(fingerprint(ctx1), fingerprint(ctx2))

    def test_automation_id_overrides_structural(self):
        # Two contexts with different structural fields but same automation_id → same fp
        ctx1 = {**BASE, "automation_id": "fixed-id", "role": "button"}
        ctx2 = {**BASE, "automation_id": "fixed-id", "role": "checkbox"}
        self.assertEqual(fingerprint(ctx1), fingerprint(ctx2))

    def test_structural_differs_on_role(self):
        ctx1 = {**BASE, "automation_id": "", "role": "button"}
        ctx2 = {**BASE, "automation_id": "", "role": "checkbox"}
        self.assertNotEqual(fingerprint(ctx1), fingerprint(ctx2))

    def test_returns_16_char_hex(self):
        fp = fingerprint(BASE)
        self.assertEqual(len(fp), 16)
        self.assertTrue(all(c in "0123456789abcdef" for c in fp))

    def test_stable_across_calls(self):
        self.assertEqual(fingerprint(BASE), fingerprint(BASE))


if __name__ == "__main__":
    unittest.main()
