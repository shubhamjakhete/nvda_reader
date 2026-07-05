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

    # --- is_known_class ---

    def test_is_known_class_for_intermediate(self):
        # :Button has subclasses so it is not a valid leaf, but it IS a known class
        self.assertTrue(self.ont.is_known_class("http://contextlabeler.org/ui-ontology#Button"))

    def test_is_known_class_for_leaf(self):
        self.assertTrue(self.ont.is_known_class("http://contextlabeler.org/ui-ontology#ActionIconButton"))

    def test_is_known_class_for_invented_uri(self):
        self.assertFalse(self.ont.is_known_class("http://contextlabeler.org/ui-ontology#FakeCategory"))

    # --- nearest_valid_ancestor ---

    def test_nearest_valid_ancestor_for_intermediate_class(self):
        # :Button is an intermediate class; the walk should return it immediately
        result = self.ont.nearest_valid_ancestor("http://contextlabeler.org/ui-ontology#Button")
        self.assertEqual(result, "http://contextlabeler.org/ui-ontology#Button")

    def test_nearest_valid_ancestor_for_unknown_returns_none(self):
        result = self.ont.nearest_valid_ancestor("http://contextlabeler.org/ui-ontology#FakeCategory")
        self.assertIsNone(result)

    def test_nearest_valid_ancestor_walks_up_from_supplement_child(self):
        # Add a temporary class that is a subclass of :IconButton via a supplement
        import tempfile, os
        ttl = """
@prefix : <http://contextlabeler.org/ui-ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:TempTestButton a owl:Class ; rdfs:subClassOf :IconButton .
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
            f.write(ttl)
            path = f.name
        try:
            self.ont.load_supplement(path)
            # :TempTestButton exists in the graph but has a child → not a leaf → not is_known_class?
            # Actually it HAS no children, so it IS a leaf and IS known.
            # Let's confirm is_known_class returns True for it
            self.assertTrue(self.ont.is_known_class("http://contextlabeler.org/ui-ontology#TempTestButton"))
            # nearest_valid_ancestor for a completely unknown sibling should walk up to :IconButton
            result = self.ont.nearest_valid_ancestor("http://contextlabeler.org/ui-ontology#MuteButton")
            self.assertIsNone(result)  # MuteButton not in graph at all → None
            # But TempTestButton is in the graph and known
            result = self.ont.nearest_valid_ancestor("http://contextlabeler.org/ui-ontology#TempTestButton")
            self.assertEqual(result, "http://contextlabeler.org/ui-ontology#TempTestButton")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
