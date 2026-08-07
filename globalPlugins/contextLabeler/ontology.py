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

    def is_known_class(self, uri: str) -> bool:
        """True if uri is any class in the UIElement subtree (leaf or intermediate)."""
        from .queries import IS_KNOWN_CLASS
        result = self._g.query(IS_KNOWN_CLASS, initBindings={"node": URIRef(uri)})
        return bool(result.askAnswer)

    def nearest_valid_ancestor(self, uri: str) -> "str | None":
        """Walk up rdfs:subClassOf from uri; return the first class inside the
        :UIElement tree, or None if the uri is entirely unknown to the graph.
        If uri is itself an intermediate class (e.g. :Button), returns uri."""
        visited = set()
        queue = [uri]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            if self.is_known_class(current):
                return current
            for parent in self._g.objects(URIRef(current), RDFS.subClassOf):
                parent_str = str(parent)
                if parent_str not in visited:
                    queue.append(parent_str)
        return None

    def ancestors(self, uri: str) -> list:
        from .queries import ANCESTORS
        return [
            (str(row.ancestor), str(row.label))
            for row in self._g.query(ANCESTORS, initBindings={"node": URIRef(uri)})
        ]

    def load_supplement(self, path: str) -> None:
        """Merge an additional Turtle ontology file into the existing graph.
        Fails silently; base ontology remains intact on any parse error.
        Calling this twice with the same file is safe since RDFLib triple stores are sets."""
        try:
            self._g.parse(path, format="turtle")
        except Exception as e:
            try:
                from logHandler import log
                log.warning(f"contextLabeler: failed to load supplement {path}: {e}")
            except Exception:
                pass
