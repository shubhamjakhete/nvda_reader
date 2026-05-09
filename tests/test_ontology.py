import unittest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins", "contextLabeler", "_vendor"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "globalPlugins"))
from contextLabeler.ontology import Ontology


class TestOntology(unittest.TestCase):
    def setUp(self):
        self.ont = Ontology.load_default()

    def test_loads_without_error(self):
        self.assertIsNotNone(self.ont)

    def test_has_leaves(self):
        leaves = self.ont.leaf_uris()
        self.assertGreater(len(leaves), 5)

    def test_known_leaf_validates(self):
        uri = "http://contextlabeler.org/ui-ontology#ActionIconButton"
        self.assertTrue(self.ont.is_valid_leaf(uri))

    def test_made_up_uri_does_not_validate(self):
        uri = "http://contextlabeler.org/ui-ontology#FakeCategory"
        self.assertFalse(self.ont.is_valid_leaf(uri))

    def test_label_for_known_leaf(self):
        uri = "http://contextlabeler.org/ui-ontology#ActionIconButton"
        self.assertEqual(self.ont.label_for(uri), "action icon button")

    def test_leaf_uris_do_not_include_intermediate_classes(self):
        leaves = self.ont.leaf_uris()
        # Button has subclasses (CommandButton, IconButton) so it must not appear
        self.assertNotIn("http://contextlabeler.org/ui-ontology#Button", leaves)

    def test_unknown_is_leaf(self):
        uri = "http://contextlabeler.org/ui-ontology#Unknown"
        self.assertTrue(self.ont.is_valid_leaf(uri))


if __name__ == "__main__":
    unittest.main()
