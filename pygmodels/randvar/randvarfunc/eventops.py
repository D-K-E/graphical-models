"""
\brief operations defined on event
"""
from pygmodels.randvar.randvarmodel.event import Event
from pygmodels.utils import is_type, is_all_type
from pygmodels.graph.graphtype.basegraph import BaseGraph
from pygmodels.graph.graphmodel.graph import Graph
from pygmodels.graph.graphmodel.digraph import DiGraph
from pygmodels.graph.graphfunc.graphsearcher import BaseGraphSearcher
from pygmodels.graph.graphfunc.graphops import BaseGraphEdgeOps
from pygmodels.graph.graphtype.edge import Edge
from typing import List, Tuple, Set, Dict
from itertools import combinations
from collections.abc import Generator


class EventBoolOps:
    """"""

    @staticmethod
    def is_incompatible(e: Event, f: Event) -> bool:
        "Biagini, Campanino, 2016, p. 6"
        is_type(e, "e", Event, True)
        is_type(f, "f", Event, True)
        #
        ef = e * f
        return all(outcome.value == 0 for outcome in ef.outcomes)

    @staticmethod
    def is_exhaustive(es: Set[Event]) -> bool:
        "Biagini, Campanino, 2016, p. 6"
        is_all_type(es, "es", Event, True)
        result = es.pop(0)
        for e in es:
            resut = result + e
        return all(outcome.value >= 1 for outcome in result.outcomes)

    @staticmethod
    def is_partition(es: Set[Event]) -> bool:
        "Biagini, Campanino, 2016, p. 6"
        exhaustive = EventBoolOps.is_exhaustive(es=es)
        return exhaustive and all(
            EventBoolOps.is_incompatible(e=ef[0], f=ef[1]) for ef in combinations(es, 2)
        )

    @staticmethod
    def is_subset_of(e: Event, f: Event) -> bool:
        """
        See Biagini, Campanino, 2016, p. 6
        E ⊂ F = E ≤ F where E <= F is I(E, F)⊂{(x, y)| x <= y}
        So basically in any combination of outputs e is smaller than f
        """
        return e <= f

    @staticmethod
    def is_logically_dependent(e: Event, es: Set[Event]) -> bool:
        """
        Check if e is logically dependent from 'es' according to
        Biagini, Campanino, 2016, p. 7
        """
        for (t, _) in EventEventSetOps.constituent_types(e=e, es=es):
            if t == 3:
                return False
        return True

    @staticmethod
    def is_logically_independent(e: Event, es: Set[Event]) -> bool:
        """
        Check if e is logically independent from 'es' according to
        Biagini, Campanino, 2016, p. 7
        """
        for (t, _) in EventEventSetOps.constituent_types(e=e, es=es):
            if t != 3:
                return False
        return True

    @staticmethod
    def is_logically_semidependent(e: Event, es: Set[Event]) -> bool:
        """
        Check if e is logically independent from 'es' according to
        Biagini, Campanino, 2016, p. 7
        """
        prev = None
        for (t, _) in EventEventSetOps.constituent_types(e=e, es=es):
            if prev is None:
                prev = t
            if t != prev:
                if not all(i in [1, 2] for i in [t, prev]):
                    return True
        return False


class EventEventOps:
    """"""

    @staticmethod
    def partition_from_event(e: Event) -> Tuple[Event, Event]:
        """
        Make a partition from event following:
        Biagini, Campanino, 2016, p. 6
        """
        is_type(e, "e", Event, True)
        e_inv = ~e
        return (e, e_inv)

    @staticmethod
    def logical_sum(e: Event, f: Event) -> Event:
        "Biagini, Campanino, 2016, p. 5"
        is_type(e, "e", Event, True)
        is_type(f, "f", Event, True)
        e_prod_f = e * f
        e_plus_f = e + f
        t = e_plus_f - e_prod_f
        return t

    @staticmethod
    def logical_product(e: Event, f: Event) -> Event:
        "Biagini, Campanino, 2016, p. 5"
        is_type(f, "f", Event, True)
        is_type(e, "e", Event, True)
        e_prod_f = e * f
        return e_prod_f

    @staticmethod
    def difference(e: Event, f: Event) -> Event:
        """"""
        is_type(e, "e", Event, True)
        is_type(f, "f", Event, True)
        e_prod_f = e * f
        d = e - e_prod_f
        return d

    @staticmethod
    def symmetric_difference(e: Event, f: Event) -> Event:
        """"""
        is_type(e, "e", Event, True)
        is_type(f, "f", Event, True)
        e_d_f = EventEventOps.difference(e, f)
        f_d_e = EventEventOps.difference(f, e)
        d = EventEventOps.logical_sum(e_d_f, f_d_e)
        return d


class EventEventSetOps:
    """"""

    @staticmethod
    def generate_constituents(es: List[Event]) -> Generator[Event]:
        """
        Generates all possible constituents for given list of events
        Biagini, Campanino, 2016, p. 6
        """
        is_all_type(es, "es", Event, True)

        def e_star(E, is_complement: bool):
            """"""
            if is_complement:
                return ~E
            else:
                return E

        def get_product(event_configuration: List[Event]) -> Event:
            """"""
            if len(event_configuration) == 1:
                return event_configuration.pop()
            #
            result = event_configuration.pop(0)
            for e in event_configuration:
                result = result * e
            return result

        e_stars = [(e_star(e, False), e_star(e, True)) for e in es]
        edges = set()
        for i in range(len(e_stars) - 1):
            p_n1, p_n2 = e_stars[i]
            c_n1, c_n2 = e_stars[i + 1]
            e1 = Edge.directed(start_node=p_n1, end_node=c_n1)
            e2 = Edge.directed(start_node=p_n1, end_node=c_n2)
            e3 = Edge.directed(start_node=p_n2, end_node=c_n1)
            e4 = Edge.directed(start_node=p_n2, end_node=c_n2)
            edges.add(e1)
            edges.add(e2)
            edges.add(e3)
            edges.add(e4)
        #
        g = BaseGraph.from_edgeset(edges)
        bfs_result1 = BaseGraphSearcher.breadth_first_search(
            g,
            n1=e_stars[0][0],
            edge_generator=lambda x: BaseGraphEdgeOps.outgoing_edges_of(g, x),
        )
        all_parents_1 = bfs_result1.props["all-parents"]
        bfs_result2 = BaseGraphSearcher.breadth_first_search(
            g,
            n1=e_stars[0][1],
            edge_generator=lambda x: BaseGraphEdgeOps.outgoing_edges_of(g, x),
        )
        all_parents_2 = bfs_result2.props["all-parents"]

        def find_all(parents, a, b):
            """
            from SO: https://stackoverflow.com/a/59604254
            """
            return (
                [a]
                if a == b
                else [y + b for x in list(parents[b]) for y in find_all(parents, a, x)]
            )

        p0_end0 = find_all(all_parents_1, a=e_stars[0][0], b=e_stars[-1][0])
        p0_end1 = find_all(all_parents_1, a=e_stars[0][0], b=e_stars[-1][1])
        p1_end0 = find_all(all_parents_1, a=e_stars[0][1], b=e_stars[-1][0])
        p1_end1 = find_all(all_parents_1, a=e_stars[0][1], b=e_stars[-1][1])
        all_paths_lst = [p0_end0, p0_end1, p1_end0, p1_end1]
        for event_paths in all_paths_lst:
            for event_path in event_paths:
                yield get_product(event_path)

    @staticmethod
    def constituent_types(e: Event, es: Set[Event]) -> Generator[Tuple[int, Event]]:
        """
        computes constituent types of the set of events 'es' vis a vis given event 'e'
        as per Biagini, Campanino, 2016, p. 7
        These types would then be used for determining if 'e' is logically
        dependent or independent or semidependent from 'es'
        """
        qs = EventEventSetOps.generate_constituents(es)
        e_inv = ~e
        for q in qs:
            if EventBoolOps.is_subset_of(q, e):
                yield (1, q)
            if EventBoolOps.is_subset_of(q, e_inv):
                yield (2, q)
            yield (3, q)
