# General Remarks about the Design of PyGModels

We have three main problems:

- Serialization of PGMs.
- Inference over PGMs.
- Learning structure of PGM from data

There are several overlaps in these problems:

- The format of serialisation of PGMs can have the same format as the learning
  problem first. Then we can build more complex PGMs on top of it.

- The inference should be able to extended to anything that has
  factors/potentials associated to it.

Functional design is to be adopted. Basically for each required set of
operations, we have a module that implements the operations and an object that
implements the necessary properties for the required operations.
The suffix `f` indicates that the module implements operations. The `type`
suffix indicate that the module contains objects that implement required
properties.


### Extension by Inheritance

The goal of extension is the use of analyzers and operators on objects.

If one wants to use `factorf` module on her object, for example the methods of
`FactorAnalyzer` or `FactorOps`, each object needs to implement `AbstractFactor`.

If one wants to use `graphf` module on her object, it needs to implement
`AbstractGraph` whose nodes implement `AbstractNode` and whose edges
implement `AbstractEdge`.

If one wants to use `pgmops` module on her object, it needs to implement
`AbstractPGM` whose nodes implement `AbstractRandomVariable`, whose edges
implement `AbstractEdge`, and whose factors implement `AbstractFactor`.

For implementation goals and milestones, see project page.

### IO

There are two goals:

- Serialize graphs
- Learn from data

Currently we only consider how to serialize graphs, particularly PGMs.

Several ideas:

- Simplest choice: Pickle it.
- Slightly harder choice: Implement a subset of graph serialization format:
  - How do you serialize a function to graph format ? Via functional strings ?

  - What are available formats ? JSON-LD, GraphML, and other more
    probabilistically related ProbXML etc.

A json-ld example would be:

```json
{
  "@context": {
    "id": {
        "@id":"http://purl.org/dc/terms/identifier",
        "@type": "xsd:string"
        },
    "data": "http://rdf.data-vocabulary.org/#ingredients",
    "node": "http://rdf.data-vocabulary.org/#yield",
    "randomvariable": "http://rdf.data-vocabulary.org/#instructions",
    "marginal_function": {
      "@id": "http://rdf.data-vocabulary.org/#step",
      "@type": "xsd:integer"
    },
    "description": "http://rdf.data-vocabulary.org/#description",
    "xsd": "https://www.w3.org/TR/xmlschema11-2"
  },
  "nodes": [
    {"type": "randomvariable", "id": "ds,kmfd",
    "fn": "function string goes on",
    "distribution": {
        "outcome-value-1": "0.4",
        "outcome-value-2": "0.3",
        "outcome-value-3": "0.3",
        "or function string goes on": "yes"
        }
    }
  ],
  "edges": [
    {"type": "directed", "data": {}, "start_id": "", "end_id": ""}
  ],
  "factors": [
  {"id": "dsafdsa", 
   "variables_in_scope": [
        "node-id-1",
        "node-id-2",
        "node-id-3",
  ], "fn": "function string goes on"
  }
  ]
}
```
