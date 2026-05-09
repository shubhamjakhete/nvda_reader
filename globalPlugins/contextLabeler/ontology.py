import os
from rdflib import Graph, RDFS, URIRef

ONTOLOGY_PATH = os.path.join(os.path.dirname(__file__), "ontology.ttl")
NS = "http://contextlabeler.org/ui-ontology#"


class Ontology:
    def __init__(self, graph: Graph):
        self._g = graph

    @classmethod
    def load_default(cls) -> "Ontology":
        g = Graph()
        g.parse(ONTOLOGY_PATH, format="turtle")
        return cls(g)

    def leaf_uris(self) -> list:
        from .queries import LEAVES
        return [str(row.leaf) for row in self._g.query(LEAVES)]

    def leaf_descriptions(self) -> list:
        from .queries import LEAVES
        results = []
        for row in self._g.query(LEAVES):
            uri = str(row.leaf)
            label = self._g.value(URIRef(uri), RDFS.label)
            comment = self._g.value(URIRef(uri), RDFS.comment)
            short = uri.rsplit("#", 1)[-1]
            desc = f":{short}"
            if label:
                desc += f" ({label}"
                if comment:
                    desc += f": {comment}"
                desc += ")"
            results.append(desc)
        return results

    def is_valid_leaf(self, uri: str) -> bool:
        from .queries import IS_LEAF
        result = self._g.query(IS_LEAF, initBindings={"leaf": URIRef(uri)})
        return bool(result.askAnswer)

    def label_for(self, uri: str) -> str:
        label = self._g.value(URIRef(uri), RDFS.label)
        return str(label) if label else uri.rsplit("#", 1)[-1]

    def ancestors(self, uri: str) -> list:
        from .queries import ANCESTORS
        return [
            (str(row.ancestor), str(row.label))
            for row in self._g.query(ANCESTORS, initBindings={"node": URIRef(uri)})
        ]
