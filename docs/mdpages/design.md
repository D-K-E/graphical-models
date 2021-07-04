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


## Extension API

### Extension by Inheritance

The goal of extension is the use of analyzers and operators on objects.

If one wants to use `factorops` module on her object, for example the methods of
`FactorAnalyzer` or `FactorOps`, her object needs to implement `AbstractFactor`.

If one wants to use `graphops` module on her object, it needs to implement
`AbstractGraph` whose nodes implement `AbstractNode` and whose edges
implement `AbstractEdge`.

If one wants to use `pgmops` module on her object, it needs to implement
`AbstractPGM` whose nodes implement `AbstractRandomVariable`, whose edges
implement `AbstractEdge`, and whose factors implement `AbstractFactor`.
