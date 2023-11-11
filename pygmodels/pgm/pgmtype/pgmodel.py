"""!
\file pgmodel.py

# Probabilistic Graphic Model with Factors

This file contains the main model that drives the inference algorithms. It
extends the graph definition by adding a new set called a set of factors.
The set of factors can be arbitrarily defined or can be deduced from edges
using independence structure assumed by the model. The #PGModel is the most
generic model, hence we do not assume a particular independence structure.

"""
import math
from typing import Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

from pygmodels.factor.factorfunc.factoralg import FactorAlgebra
from pygmodels.factor.factorfunc.factoranalyzer import FactorAnalyzer
from pygmodels.factor.factorfunc.factorops import FactorOps
from pygmodels.factor.factortype.abstractfactor import AbstractFactor
from pygmodels.factor.factortype.basefactor import BaseFactor
from pygmodels.graph.ganalysis.graphanalyzer import (
    BaseGraphAnalyzer,
    BaseGraphBoolAnalyzer,
    BaseGraphNodeAnalyzer,
    BaseGraphNumericAnalyzer,
)
from pygmodels.graph.graphmodel.graph import Graph
from pygmodels.graph.graphops.graphalg import BaseGraphAlgOps
from pygmodels.graph.graphops.graphops import (
    BaseGraphBoolOps,
    BaseGraphEdgeOps,
    BaseGraphNodeOps,
    BaseGraphOps,
)
from pygmodels.graph.graphtype.edge import Edge
from pygmodels.graph.graphtype.node import Node
from pygmodels.pgm.pgmtype.randomvariable import NumCatRVariable, NumericValue
from pygmodels.utils import is_all_type


class PGModel(Graph):
    """"""

    def __init__(
        self,
        gid: str,
        nodes: Set[NumCatRVariable],
        edges: Set[Edge],
        factors: Optional[Set[AbstractFactor]] = None,
        data={},
    ):
        """!
        \brief constructor for a generic Probabilistic Graphical Model

        The generic model that extends the #Graph definition by adding a new
        set, called set of factors.
        Most of the parameters are documented in #Graph.
        """
        super().__init__(gid=gid, data=data, nodes=nodes, edges=edges)
        is_all_type(factors, "factors", BaseFactor, True)
        if factors is None:
            fs: Set[BaseFactor] = set()
            for e in self.E:
                estart = e.start()
                eend = e.end()
                sdata = estart.data()
                edata = eend.data()
                evidences = set()
                if "evidence" in sdata:
                    evidences.add((estart.id(), sdata["evidence"]))
                if "evidence" in edata:
                    evidences.add((eend.id(), edata["evidence"]))
                f = BaseFactor(gid=str(uuid4()), scope_vars=set([estart, eend]))
                if len(evidences) != 0:
                    f = FactorOps.reduced_by_value(f, evidences)
                fs.add(f)
            self.Fs = fs
        else:
            self.Fs = factors
