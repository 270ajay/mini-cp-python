"""This code is a translation of the original code in java.
Original code: https://github.com/minicp/minicp
Online course: https://www.edx.org/learn/computer-programming/universite-catholique-de-louvain-constraint-programming
/*
 * mini-cp is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License  v3
 * as published by the Free Software Foundation.
 *
 * mini-cp is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY.
 * See the GNU Lesser General Public License  for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mini-cp. If not, see http://www.gnu.org/licenses/lgpl-3.0.en.html
 *
 * Copyright (c)  2018. by Laurent Michel, Pierre Schaus, Pascal Van Hentenryck
 */
"""

import abc
from typing import Callable

from mini_cp.engine import exceptions, int_var, state

_MAX_VALUE = 2147483647


class Objective(abc.ABC):
    """Objective object to be used in the
    DFSearch optimize(Objective) for implementing the
    branch and bound depth first search.
    """

    @abc.abstractmethod
    def tighten(self) -> "None":
        """Method called each time a solution is found during
        the search to let the tightening of the primal bound
        occur such that the next found solution is better.
        """


class Minimize(Objective):
    """Minimization objective function."""

    def __init__(self, x: "int_var.IntVar"):
        self._bound: "int" = _MAX_VALUE
        self._x: "int_var.IntVar" = x
        self._x.get_solver().on_fix_point(lambda: x.remove_above(self._bound))

    def tighten(self) -> "None":
        if not self._x.is_fixed():
            raise RuntimeError("Objective not fixed")
        self._bound = self._x.max() - 1

    def __str__(self) -> "str":
        return f"Objective: {self._x.min()}"


class SearchStatistics:
    """Statistics collected during the execution of
    DFSearch solve() and DFSearch optimize(Objective)
    """

    def __init__(self):
        self._n_failures: "int" = 0
        self._n_nodes: "int" = 0
        self._n_solutions: "int" = 0
        self._completed: "bool" = False

    def __str__(self) -> "str":
        return (
            f"\n\t#choice: {self._n_nodes}\n\t#fail: "
            f"{self._n_failures}\n\t#sols: "
            f"{self._n_solutions}\n\tcompleted: "
            f"{self._completed}\n"
        )

    def incr_failures(self) -> "None":
        self._n_failures += 1

    def incr_nodes(self) -> "None":
        self._n_nodes += 1

    def incr_solutions(self) -> "None":
        self._n_solutions += 1

    def set_completed(self) -> "None":
        self._completed = True

    def number_of_failures(self) -> "int":
        return self._n_failures

    def number_of_nodes(self) -> "int":
        return self._n_nodes

    def number_of_solutions(self) -> "int":
        return self._n_solutions

    def is_completed(self) -> "bool":
        return self._completed


class DFSListener(abc.ABC):

    def solution(self, p_id: "int", id: "int", position: "int") -> "None":
        pass

    def fail(self, p_id: "int", id: "int", position: "int") -> "None":
        pass

    def branch(
        self, p_id: "int", id: "int", position: "int", n_childs: "int"
    ) -> "None":
        pass


class Sequencer:
    """Sequential Search combinator that linearly
    considers a list of branching generator.
    One branching of this list is executed when all
    the previous ones are exhausted, that is they
    an empty array.
    """

    def __init__(self, branching: "list[Callable[[], list[Callable[[], None]]]]"):
        """Creates a sequential search combinator.
        'branching': the sequence of branching
        """
        self._branching: "list[Callable[[], list[Callable[[], None]]]]" = branching

    def __call__(self) -> "list[Callable[[], None]]":
        for i in range(len(self._branching)):
            alts = self._branching[i]()
            if len(alts) != 0:
                return alts
        return []


class DFSearch:
    """Depth First Search Branch and Bound implementation."""

    def __init__(
        self,
        sm: "state.StateManager",
        branching: "Callable[[], list[Callable[[], None]]]",
    ):
        """Creates a Depth First Search object with a given branching
        that defines the search tree dynamically.
        'sm': the state manager that will be saved and restored at each
        node of the search tree
        'branching': a generator of closures in charge of defining the ordered
        children nodes at each node of the depth-first-search tree.
        When it returns an empty array, a solution is found.
        Backtrack occurs when an InconsistencyException is thrown.
        """
        self._sm: "state.StateManager" = sm
        self._branching: "Callable[[], list[Callable[[], None]]]" = branching
        self._curr_node_id_id: "int" = 0
        self._dfs_listeners: "list[DFSListener]" = []

    def on_solution(self, listener: "Callable[[], None]") -> "None":
        """Adds a listener that is called on each solution.
        'listener': the closure to be called whenever a solution is found
        """

        class NewDFSListener(DFSListener):
            def solution(self, p_id: "int", id: "int", position: "int") -> "None":
                listener()

        self._dfs_listeners.append(NewDFSListener())

    def add_listener(self, listener: "DFSListener") -> "None":
        self._dfs_listeners.append(listener)

    def on_failure(self, listener: "Callable[[], None]") -> "None":
        """Adds a listener that is called whenever a failure occurs
        and the search backtracks.
        This happens when an InconsistencyException is thrown
        when executing the closure generated by the branching.
        'listener': the closure to be called whenever a failure occurs and
        the search need to backtrack.
        """

        class NewDFSListener(DFSListener):
            def fail(self, p_id: "int", id: "int", position: "int") -> "None":
                listener()

        self._dfs_listeners.append(NewDFSListener())

    def _notify_solution(
        self, parent_id: "int", node_id: "int", position: "int"
    ) -> "None":
        for listener in self._dfs_listeners:
            listener.solution(parent_id, node_id, position)

    def _notify_failure(
        self, parent_id: "int", node_id: "int", position: "int"
    ) -> "None":
        for listener in self._dfs_listeners:
            listener.fail(parent_id, node_id, position)

    def _notify_branch(
        self, parent_id: "int", node_id: "int", position: "int", n_childs: "int"
    ) -> "None":
        for listener in self._dfs_listeners:
            listener.branch(parent_id, node_id, position, n_childs)

    def _solve(
        self,
        statistics: "SearchStatistics",
        limit: "Callable[[SearchStatistics], bool]",
    ) -> "SearchStatistics":
        self._curr_node_id_id = 0

        def callback() -> "None":
            try:
                self._dfs(statistics, limit, -1, -1)
                statistics.set_completed()
            except exceptions.StopSearchException:
                pass
            except RecursionError:
                raise NotImplementedError(
                    "Dfs with explicit stack needed to pass this test"
                )

        self._sm.with_new_state(callback)
        return statistics

    def solve(
        self, limit: "Callable[[SearchStatistics], bool]" = None
    ) -> "SearchStatistics":
        """If limit is None:
        Effectively start a depth first search
        looking for every solution.
        Else:
        Effectively starts a depth first search with a given callback
        called at each node to stop the search when it becomes true.
        'limit': a callback called at each node that stops the search
        when it becomes true.
        Returns an object with the statistics on the search
        """
        statistics = SearchStatistics()
        if limit is not None:
            return self._solve(statistics, limit)
        else:
            return self._solve(statistics, lambda stats: False)

    def solve_subject_to(
        self,
        limit: "Callable[[SearchStatistics], bool]",
        subject_to: "Callable[[], None]",
    ) -> "SearchStatistics":
        """Executes a closure prior to effectively
        starting a depth first search with a
        given callback called at each node to stop the
        search when it becomes true.
        The state manager saves the state before
        executing the closure and restores it
        after the search.
        Any InconsistencyException that may
        be thrown when executing the closure is also
        caught.
        'limit': a callback called at each node that stops
        the search when it becomes true
        'subject_to': the closure to execute prior to the search starts
        Return an object with the statistics on the search
        """
        statistics = SearchStatistics()

        def callback() -> "None":
            try:
                subject_to()
                self._solve(statistics, limit)
            except exceptions.InconsistencyException:
                pass

        self._sm.with_new_state(callback)
        return statistics

    def optimize(
        self, obj: "Objective", limit: "Callable[[SearchStatistics], bool]" = None
    ) -> "SearchStatistics":
        """If limit is None:
        Effectively start a branch and bound
        depth first search with a given objective.
        'obj': the objective to optimize that is tightened each time a new
        solution is found
        Returns an object with the statistics on the search
        Else:
        Effectively

        """
        statistics = SearchStatistics()
        self.on_solution(lambda: obj.tighten())
        if limit is not None:
            return self._solve(statistics, limit)
        else:
            return self._solve(statistics, lambda stats: False)

    def optimize_subject_to(
        self,
        obj: "Objective",
        limit: "Callable[[SearchStatistics], bool]",
        subject_to: "Callable[[], None]",
    ) -> "SearchStatistics":
        """Executes a closure prior to effectively
        starting a branch and bound depth first search with
        a given objective to optimize and a given callback
        called at each node to stop the search when it becomes true.
        The state manager saves the state before
        executing the closure and restores it after the search.
        Any InconsistencyException that may be thrown when
        executing the closure is also caught.
        'obj': the objective to optimize that is tightened each time
        a new solution is found
        'limit': a predicate called at each node that stops the search
        when it becomes true
        'subject_to': the closure to execute prior to the search starts
        Returns an object with the statistics on the search
        """
        statistics = SearchStatistics()

        def callback() -> "None":
            try:
                subject_to()
                statistics = self.optimize(obj, limit)
            except exceptions.InconsistencyException:
                pass

        self._sm.with_new_state(callback)
        return statistics

    def _dfs(
        self,
        statistics: "SearchStatistics",
        limit: "Callable[[SearchStatistics], bool]",
        parent_id: "int",
        position: "int",
    ) -> "None":

        def callback() -> "None":
            try:
                statistics.incr_nodes()
                b()
                self._dfs(statistics, limit, node_id, p)
            except exceptions.InconsistencyException:
                self._curr_node_id_id += 1
                statistics.incr_failures()
                self._notify_failure(parent_id, node_id, p)

        if limit(statistics):
            raise exceptions.StopSearchException()

        branches = self._branching()
        node_id = self._curr_node_id_id
        self._curr_node_id_id += 1

        if len(branches) == 0:
            statistics.incr_solutions()
            self._notify_solution(parent_id, node_id, position)
        else:
            self._notify_branch(parent_id, node_id, position, len(branches))
            pos = 0
            for b in branches:
                p = pos
                self._sm.with_new_state(callback)
                pos += 1


class LimitedDiscrepancyBranching:
    """Branching combinator that ensure that the alternatives
    created are always within the discrepancy limit.
    The discrepancy of an alternative generated for a given
    node is the distance from the left most alternative.
    The discrepancy of a node is the sum of the discrepancy of
    its ancestors.
    """

    def __init__(
        self,
        branching: "Callable[[], list[Callable[[], None]]]",
        max_discrepancy: "int",
    ):
        """Creates a discrepancy combinator on a given branching.
        'branching': the branching on which to apply the discrepancy combinator
        'max_discrepancy': the maximum discrepancy limit. Any node exceeding that
        limit is pruned.
        """
        if max_discrepancy < 0:
            raise ValueError("Max discrepancy should be >= 0")
        self._bs: "Callable[[], list[Callable[[], None]]]" = branching
        self._max_d: "int" = max_discrepancy
        self._cur_d: "int" = 0

    def __call__(self) -> "list[Callable[[], None]]":
        # Hint:
        # Filter-out alternatives from bs that would exceed max_d
        # Therefore wrap each alternative
        # such that the call method of the wrapped alternatives
        # sets the cur_d depending on its position
        # cur_d = d + 0 for alts[0],...,+i for alts[i]
        raise NotImplementedError("LimitedDiscrepancy")
