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

In order for an object to be usable by Factor


The API of this library expects that any third party object implements the
`AbstractGraph` object in order to become inferable. 
It has a very simple structure.

```python

from gmodels.gtypes.abstractobj import AbstractGraph

class MyGraph(AbstractGraph):

    def __init__(self, *args, **kwargs):
        ""

    @property
    def V(self) -> Dict[str, AbstractNode]:
        "output the vertex set as id: vertex dictionary"

    @property
    def E(self) -> Dict[str, AbstractEdge]:
        "output the edge set as id: vertex dictionary"

    def is_neighbour_of(self, n1: AbstractNode, n2: AbstractNode) -> bool:
        "check if any two given nodes are a neighbour"

    def is_trivial(self) -> bool:
        "check if graph is trivial"


    def order(self) -> int:
        "compute order, number of vertices, of graph"

```
