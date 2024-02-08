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

from typing import Callable

import pytest

from mini_cp.cp import branching_scheme, factory
from mini_cp.engine import constraint, exceptions, int_var, search, solver, state


def test_conflict_ordering_search() -> "None":

    def variable_selector() -> "int_var.IntVar":
        # select first unfixed variable in x
        for z in x:
            if not z.is_fixed():
                return z

    def limit(statistics: "search.SearchStatistics") -> "bool":
        if statistics.number_of_failures() > 4:
            n_fixed = 0
            for i in range(4):
                if x[i].is_fixed():
                    n_fixed += 1

            assert n_fixed != 4, (
                "Conflict ordering should take the upper hands on "
                "the search provided and branch on the variables causing "
                "the most recent conflicts"
            )

        return False

    try:
        cp = factory.make_solver()
        x = factory.make_int_var_array(cp, 8, 8)
        for i in range(4, 8):
            x[i].remove_above(2)

        # Apply AllDifferent on the four last variables.
        # Ofcourse,this cannot work!
        four_last = [x[i] for i in range(4, 8)]
        cp.post(factory.all_different(four_last))

        dfs = search.DFSearch(
            cp.get_state_manager(),
            branching_scheme.conflict_ordering_search(
                variable_selector, lambda v: v.min()  # select smallest value
            ),
        )

        stats = dfs.solve(limit)

        assert stats.number_of_solutions() == 0
        assert stats.number_of_failures() == 30
        assert stats.number_of_nodes() == 58

    except NotImplementedError:
        pass


def test_conflict_ordering_search2() -> "None":
    def variable_selector() -> "int_var.IntVar":
        # select first unfixed variable in x
        for z in x:
            if not z.is_fixed():
                return z

    try:
        cp = factory.make_solver()
        x = factory.make_int_var_array(cp, 10, 10)
        for i in range(5, 10):
            x[i].remove_above(3)

        # Apply AllDifferent on the five last variables.
        # Ofcourse, this cannot work!
        five_last = [x[i] for i in range(5, 10)]
        cp.post(constraint.AllDifferentBinary(five_last))
        dfs = search.DFSearch(
            cp.get_state_manager(),
            branching_scheme.conflict_ordering_search(
                variable_selector, lambda v: v.min()  # select smallest value
            ),
        )

        stats = dfs.solve()
        assert stats.number_of_solutions() == 0
        assert stats.number_of_failures() == 144
        assert stats.number_of_nodes() == 286

    except NotImplementedError:
        pass


@pytest.mark.parametrize("state_manager_class", [state.Trailer, state.Copier])
def test_dfs_search_example0(state_manager_class: "state.StateManager") -> "None":

    SAVE = -1
    RESTORE = -2

    class TempStateManager(state_manager_class):

        def __init__(self):
            super().__init__()
            self.operations: "list[int]" = []
            self.last_save_level: "int" = -1
            self.start_level: "int" = -1

        def perform_op(self, character: "int"):
            if self.start_level < 0:
                self.start_level = self.get_level()
                if self.last_save_level == self.start_level:
                    self.operations.append(SAVE)

            self.operations.append(character)

        def save_state(self) -> "None":
            super().save_state()
            if self.start_level >= 0:
                self.operations.append(SAVE)
            else:
                self.last_save_level = self.get_level()

        def restore_state(self) -> "None":
            if self.start_level >= 0 and self.get_level() >= self.start_level:
                self.operations.append(RESTORE)
            super().restore_state()

    sm = TempStateManager()
    alternative = sm.make_state_int(0)

    def callback() -> "list[Callable[[], None]]":
        if alternative.value() == 0:
            return [
                lambda: sm.perform_op(alternative.set_value(ord("A"))),
                lambda: sm.perform_op(alternative.set_value(ord("B"))),
                lambda: sm.perform_op(alternative.set_value(ord("C"))),
            ]
        elif alternative.value() == ord("A"):
            return [
                lambda: sm.perform_op(alternative.set_value(ord("D"))),
                lambda: sm.perform_op(alternative.set_value(ord("E"))),
            ]
        elif alternative.value() == ord("C"):
            return [
                lambda: sm.perform_op(alternative.set_value(ord("F"))),
                lambda: sm.perform_op(alternative.set_value(ord("G"))),
            ]

        return []

    dfs = search.DFSearch(sm, callback)
    stats = dfs.solve()
    assert stats.number_of_nodes() == 7
    assert stats.number_of_solutions() == 5
    assert stats.number_of_failures() == 0

    if len(sm.operations) == 15:
        assert sm.operations == [
            SAVE,
            ord("A"),
            SAVE,
            ord("D"),
            RESTORE,
            ord("E"),
            RESTORE,
            SAVE,
            ord("B"),
            RESTORE,
            ord("C"),
            SAVE,
            ord("F"),
            RESTORE,
            ord("G"),
        ]

    else:
        assert len(sm.operations) == 21
        assert sm.operations == [
            SAVE,
            ord("A"),
            SAVE,
            ord("D"),
            RESTORE,
            SAVE,
            ord("E"),
            RESTORE,
            RESTORE,
            SAVE,
            ord("B"),
            RESTORE,
            SAVE,
            ord("C"),
            SAVE,
            ord("F"),
            RESTORE,
            SAVE,
            ord("G"),
            RESTORE,
            RESTORE,
        ]


@pytest.mark.parametrize("sm", [state.Trailer(), state.Copier()])
def test_dfs_search_example1(sm: "state.StateManager") -> "None":
    def callback() -> "list[Callable[[], None]]":
        if i.value() >= len(values):
            return []
        else:
            val = i.value()
            return [
                lambda: branch(val, 0),  # left branch
                lambda: branch(val, 1),  # right branch
            ]

    def branch(index: "int", value: "int") -> "None":
        values[index] = value
        i.set_value(index + 1)

    i = sm.make_state_int(0)
    values = [0] * 3
    dfs = search.DFSearch(sm, callback)
    stats = dfs.solve()
    assert stats.number_of_solutions() == 8
    assert stats.number_of_failures() == 0
    assert stats.number_of_nodes() == 8 + 4 + 2


@pytest.mark.parametrize("sm", [state.Trailer(), state.Copier()])
def test_dfs_search_example3(sm: "state.StateManager") -> "None":
    def callback() -> "list[Callable[[], None]]":
        if i.value() >= len(values):
            return []
        else:
            val = i.value()
            return [
                lambda: branch(val, 0),  # left branch
                lambda: branch(val, 1),  # right branch
            ]

    def branch(index: "int", value: "int") -> "None":
        values[index] = value
        i.set_value(index + 1)

    i = sm.make_state_int(0)
    values = [0] * 3
    dfs = search.DFSearch(sm, callback)
    stats = dfs.solve(lambda stat: stat.number_of_solutions() >= 1)
    assert stats.number_of_solutions() == 1


@pytest.mark.parametrize("sm", [state.Trailer(), state.Copier()])
def test_dfs(sm: "state.StateManager") -> "None":
    def callback() -> "list[Callable[[], None]]":
        if i.value() >= len(values):
            return []
        else:
            val = i.value()
            return [
                lambda: branch(val, False),  # left branch
                lambda: branch(val, True),  # right branch
            ]

    def branch(index: "int", value: "bool") -> "None":
        values[index] = value
        i.set_value(index + 1)

    def increment() -> "None":
        n_sols[0] += 1

    i = sm.make_state_int(0)
    values = [False] * 4
    dfs = search.DFSearch(sm, callback)
    n_sols = [0]
    dfs.on_solution(lambda: increment())

    stats = dfs.solve()
    assert n_sols[0] == 16
    assert stats.number_of_solutions() == 16
    assert stats.number_of_failures() == 0
    assert stats.number_of_nodes() == 16 + 8 + 4 + 2


@pytest.mark.parametrize("sm", [state.Trailer(), state.Copier()])
def test_dfs_search_limit(sm: "state.StateManager") -> "None":
    def callback() -> "list[Callable[[], None]]":
        if i.value() >= len(values):
            return [lambda: raise_exception()]
        else:
            return [
                lambda: branch(i, False),  # left branch
                lambda: branch(i, True),  # right branch
            ]

    def raise_exception() -> "None":
        raise exceptions.InconsistencyException()

    def branch(i: "state.StateInt", value: "bool") -> "None":
        values[i.value()] = value
        i.increment()

    i = sm.make_state_int(0)
    values = [False] * 4
    dfs = search.DFSearch(sm, callback)
    stats = dfs.solve(lambda stat: stat.number_of_failures() >= 3)

    assert stats.number_of_solutions() == 0
    assert stats.number_of_failures() == 3


@pytest.mark.parametrize("sm", [state.Trailer(), state.Copier()])
def test_deep_dfs(sm: "state.StateManager") -> "None":
    def callback() -> "list[Callable[[], None]]":
        if i.value() >= len(values):
            return []
        else:
            return [
                lambda: branch(i, False),  # left branch
                lambda: branch(i, True),  # right branch
            ]

    def branch(i: "state.StateInt", value: "bool") -> "None":
        values[i.value()] = value
        i.increment()

    i = sm.make_state_int(0)
    values = [False] * 10000
    dfs = search.DFSearch(sm, callback)
    try:
        # stop search after 1 solution (only left most branch)
        stats = dfs.solve(lambda stat: stat.number_of_solutions() >= 1)
        assert stats.number_of_solutions() == 1
    except NotImplementedError:
        pass


@pytest.mark.parametrize("sm", [state.Trailer(), state.Copier()])
def test_check_inconsistencies_managed_correctly(sm: "state.StateManager") -> "None":

    def callback() -> "list[Callable[[], None]]":
        if values[0] >= 100:
            return []
        else:
            return [left_branch, right_branch]

    def left_branch() -> "None":
        values[0] += 1
        if values[0] == 1:
            raise exceptions.InconsistencyException()
        # this should never happen in a left branch!
        assert values[0] != 2

    def right_branch() -> "None":
        values[0] += 1

    values = [0] * 3
    dfs = search.DFSearch(sm, callback)
    dfs.solve()


# /**
#  * Example given on the slide of the course
#  * Nodes 3, 5 and 6 results in a failure
#  * On node 8, x should be chosen instead of y as it resulted in a conflict
#  *
#  *                        +------------1------------+
#  *                    y=0 |                         | y!=0
#  *                  +----2----+                +----7
#  *              x=0 |         | x!=0       x=0 |
#  *                  3    +----4----+           8
#  *                   x=1 |         | x!=1
#  *                       5         6
#  *
#  */


@pytest.mark.parametrize("by_copy", [False, True])
def test_last_conflict_search(by_copy: "bool") -> "None":
    class ANewConstraint(constraint.AbstractConstraint):

        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)
            self.node: "int" = 1
            self.throw_inconsistency: "set[int]" = {3, 5, 6}

        def post(self) -> "None":
            x.propagate_on_domain_change(self)
            y.propagate_on_domain_change(self)

        def propagate(self) -> "None":
            n = self.node
            if n in self.throw_inconsistency:
                raise exceptions.InconsistencyException()
            if n == 8:
                assert x.is_fixed() is True
                assert x.min() == 0

    def variable_selector() -> "int_var.IntVar":
        # select first unfixed variable in variables
        for z in variables:
            if not z.is_fixed():
                return z

    def limit(statistics: "search.SearchStatistics") -> "bool":
        if statistics.number_of_solutions() >= 7:
            assert x.is_fixed() is True
            assert x.min() == 0
            return True
        return False

    try:
        cp = factory.make_solver(by_copy)
        x = factory.make_int_var(cp, sz=5)  # x: {0..4}
        y = factory.make_int_var(cp, sz=5)  # y: {0..4}
        variables = [y, x]
        cp.post(ANewConstraint(cp))

        dfs = search.DFSearch(
            cp.get_state_manager(),
            branching_scheme.last_conflict(
                variable_selector, lambda v: v.min()  # select smallest value
            ),
        )

        # stops the search after the end of the example, and checks the
        # value of x
        dfs.solve(limit)
    except NotImplementedError:
        pass


@pytest.mark.parametrize("by_copy", [False, True])
def test_last_conflict_search_example1(by_copy: "bool") -> "None":
    def variable_selector() -> "int_var.IntVar":
        # select first unfixed variable in x
        for z in x:
            if not z.is_fixed():
                return z

    def limit(statistics: "search.SearchStatistics") -> "bool":
        if statistics.number_of_nodes() >= 61 and statistics.number_of_nodes() <= 64:
            n_fixed = 0
            for i in range(4):
                if x[i].is_fixed():
                    n_fixed += 1

            assert n_fixed != 4, (
                "Last conflict should take the upper hands on "
                "the search provided and branch first on the "
                "variable causing the latest conflict"
            )

        return False

    try:
        cp = factory.make_solver(by_copy)
        x = factory.make_int_var_array(cp, 8, 8)
        for i in range(4, 8):
            x[i].remove_above(2)

        # apply AllDifferent on the four last variables.
        # Ofcourse, this cannot work!
        four_last = [x[i] for i in range(4, 8)]
        cp.post(constraint.AllDifferentBinary(four_last))

        dfs = search.DFSearch(
            cp.get_state_manager(),
            branching_scheme.last_conflict(
                variable_selector, lambda v: v.min()  # select smallest value
            ),
        )

        stats = dfs.solve(limit)
        assert stats.number_of_solutions() == 0
        assert stats.number_of_failures() == 70
        assert stats.number_of_nodes() == 138
    except NotImplementedError:
        pass


@pytest.mark.parametrize("by_copy", [False, True])
def test_last_conflict_search_example2(by_copy: "bool") -> "None":
    def variable_selector() -> "int_var.IntVar":
        # select first unfixed variable in x
        for z in x:
            if not z.is_fixed():
                return z

    try:
        cp = factory.make_solver(by_copy)
        x = factory.make_int_var_array(cp, 10, 10)
        for i in range(5, 10):
            x[i].remove_above(3)

        # Apply AllDifferent on the five last variables.
        # Ofcourse, this cannot work!
        five_last = [x[i] for i in range(5, 10)]
        cp.post(constraint.AllDifferentBinary(five_last))

        dfs = search.DFSearch(
            cp.get_state_manager(),
            branching_scheme.last_conflict(
                variable_selector, lambda v: v.min()  # # select smallest value
            ),
        )

        stats = dfs.solve()
        assert stats.number_of_solutions() == 0
        assert stats.number_of_failures() == 894
        assert stats.number_of_nodes() == 1786

    except NotImplementedError:
        pass


@pytest.mark.parametrize("sm", [state.Trailer(), state.Copier()])
def test_limited_discrepancy_branching(sm: "state.StateManager") -> "None":
    def callback() -> "list[Callable[[], None]]":
        if i.value() >= len(values):
            return []
        else:
            return [lambda: branch(i, 0), lambda: branch(i, 1)]

    def branch(i: "state.StateInt", value: "int") -> "None":
        values[i.value()] = value
        i.increment()

    def solution_callback() -> "None":
        n1 = 0
        for k in range(len(values)):
            n1 += values[k]
        assert n1 <= 2

    try:
        i = sm.make_state_int(0)
        values = [0] * 4
        bs_discrepancy = search.LimitedDiscrepancyBranching(callback, 2)
        dfs = search.DFSearch(sm, bs_discrepancy)
        dfs.on_solution(solution_callback)

        stats = dfs.solve()
        assert stats.number_of_solutions() == 11
        assert stats.number_of_failures() == 0
        assert stats.number_of_nodes() == 24  # root node does not count
    except NotImplementedError:
        pass


class TestSequencer:

    @classmethod
    def setup_class(cls) -> "None":
        cls.state = 0

    def test_example1(self) -> "None":
        """Exert the Sequencer in a BFS-way"""
        try:
            seq = search.Sequencer(
                [self._fake_sequencer0, self._fake_sequencer1, self._fake_sequencer2]
            )
            self.state = 0
            branches = seq()
            assert len(branches) == 2
            branches[0]()
            assert self.state == 1
            branches[1]()
            assert self.state == 2

            self.state = 1
            branches = seq()
            assert len(branches) == 2
            branches[0]()
            assert self.state == 3
            branches[1]()
            assert self.state == 4

            self.state = 2
            branches = seq()
            assert len(branches) == 2
            branches[0]()
            assert self.state == 5
            branches[1]()
            assert self.state == 6

            self.state = 4
            branches = seq()
            assert len(branches) == 3
            branches[0]()
            assert self.state == 7
            branches[1]()
            assert self.state == 8
            branches[2]()
            assert self.state == 9

            for s in [3, 5, 6, 7, 8, 9]:
                self.state = s
                branches = seq()
                assert len(branches) == 0

        except NotImplementedError:
            pass

    def test_example2(self) -> "None":
        """Exert the Sequencer in a BFS-way"""
        try:
            seq = search.Sequencer(
                [self._fake_sequencer0, self._fake_sequencer1, self._fake_sequencer2]
            )
            self.state = 0
            branches = seq()
            assert len(branches) == 2
            branches[0]()
            assert self.state == 1
            branches[1]()
            assert self.state == 2

            self.state = 1
            branches = seq()
            assert len(branches) == 2
            branches[0]()
            assert self.state == 3
            branches[1]()
            assert self.state == 4

            self.state = 4
            branches = seq()
            assert len(branches) == 3
            branches[0]()
            assert self.state == 7
            branches[1]()
            assert self.state == 8
            branches[2]()
            assert self.state == 9

            self.state = 2
            branches = seq()
            assert len(branches) == 2
            branches[0]()
            assert self.state == 5
            branches[1]()
            assert self.state == 6

            for s in [3, 5, 6, 7, 8, 9]:
                self.state = s
                branches = seq()
                assert len(branches) == 0

        except NotImplementedError:
            pass

    def _change_state(self, val: "int") -> "None":
        self.state = val

    def _fake_sequencer0(self) -> "list[Callable[[], None]]":
        if self.state == 0:
            return [lambda: self._change_state(1), lambda: self._change_state(2)]
        else:
            return []

    def _fake_sequencer1(self) -> "list[Callable[[], None]]":
        if self.state == 1:
            return [lambda: self._change_state(3), lambda: self._change_state(4)]
        elif self.state == 2:
            return [lambda: self._change_state(5), lambda: self._change_state(6)]
        else:
            return []

    def _fake_sequencer2(self) -> "list[Callable[[], None]]":
        if self.state == 2:
            return [lambda: self._change_state(10)]
        if self.state == 4:
            return [
                lambda: self._change_state(7),
                lambda: self._change_state(8),
                lambda: self._change_state(9),
            ]
        else:
            return []
