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
