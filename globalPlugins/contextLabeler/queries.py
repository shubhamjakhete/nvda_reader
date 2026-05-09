PREFIXES = """
PREFIX : <http://contextlabeler.org/ui-ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
"""

LEAVES = PREFIXES + """
SELECT ?leaf WHERE {
  ?leaf a owl:Class .
  ?leaf rdfs:subClassOf+ :UIElement .
  FILTER NOT EXISTS { ?child rdfs:subClassOf ?leaf }
}
"""

IS_LEAF = PREFIXES + """
ASK {
  ?leaf a owl:Class .
  ?leaf rdfs:subClassOf+ :UIElement .
  FILTER NOT EXISTS { ?child rdfs:subClassOf ?leaf }
}
"""

ANCESTORS = PREFIXES + """
SELECT ?ancestor ?label WHERE {
  ?node rdfs:subClassOf+ ?ancestor .
  ?ancestor rdfs:label ?label .
}
"""
