# Ontology Guide

## What the ontology is

`globalPlugins/contextLabeler/ontology.ttl` is a hand-edited RDF/Turtle file that defines the complete vocabulary of UI element categories the add-on is allowed to produce. Claude must return a URI from this file; anything else is rejected.

## Structure

The hierarchy looks like this (indentation = subClassOf):

```
UIElement
├── Control
│   ├── Button
│   │   ├── CommandButton         ← leaf
│   │   └── IconButton
│   │       ├── ActionIconButton  ← leaf
│   │       └── ToggleIconButton  ← leaf
│   ├── Input
│   │   ├── TextInput             ← leaf
│   │   └── SearchInput           ← leaf
│   └── Selector
│       ├── Dropdown              ← leaf
│       ├── Checkbox              ← leaf
│       └── RadioButton           ← leaf
├── Display
│   ├── Image
│   │   ├── DecorativeImage       ← leaf
│   │   ├── InformativeImage      ← leaf
│   │   └── FunctionalImage       ← leaf
│   └── Icon
│       ├── StatusIcon            ← leaf
│       └── BrandIcon             ← leaf
├── Navigation
│   ├── Link                      ← leaf
│   ├── Tab                       ← leaf
│   └── MenuItem                  ← leaf
└── Unknown                       ← leaf (fallback)
```

Only leaf classes (those with no subclasses) can be returned by Claude. Intermediate classes like `Button` and `Icon` exist only for hierarchy; the SPARQL query excludes them.

## Adding a new category

1. Add the new class to `ontology.ttl`. Example:
   ```turtle
   :SliderControl a owl:Class ;
       rdfs:subClassOf :Control ;
       rdfs:label "slider control"@en ;
       rdfs:comment "Range input that adjusts a value."@en .
   ```

2. That's it. No Python changes needed. The SPARQL LEAVES query picks it up automatically.

3. Verify with `python -m unittest tests/test_ontology.py` — add a test for the new leaf if you want coverage.

## Namespace

All classes use the prefix `http://contextlabeler.org/ui-ontology#`. In Turtle, this is declared as `@prefix : <...> .` so you can write `:SliderControl` as shorthand.
