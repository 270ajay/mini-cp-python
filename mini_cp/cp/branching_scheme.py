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

 Factory for search procedures.

 A typical custom search on an array of variable {q} is illustrated next

 def callback() -> "list[Callable[[], None]]":
     idx = -1; // index of the first variable that is not fixed
     for k in range(len(q)):
         if(q[k].size() > 1):
             idx=k
             break
     if(idx == -1):
         return []
     else:
         qi = q[idx];
         v = qi.min();
         left = lambda: factory.equal(qi, v);
         right = lambda: factory.notEqual(qi, v);
         return [left, right];

 search = factory.make_dfs(cp, callback)

 See factory make_dfs(Solver, Callable)
"""

from typing import Callable, TypeVar

from mini_cp.cp import factory
from mini_cp.engine import int_var, search

_T = TypeVar("_T")
_N = TypeVar("_N")

# Constant that should be returned to notify the
# solver that there are no branches
# to create any more and that the current state should
# be considered as a solution
# See factory make_dfs(Solver, Callable)
_EMPTY = []


def select_min(
    x: "list[_T]", p: "Callable[[_T], bool]", f: "Callable[[_T], _N]"
) -> "_T":
    """Minimum selector.
    Example of usage.

    xs = select_min(x, lambda xi: xi.size() > 1, lambda xi: xi.size())

    'x': the array on which the minimum value is searched
    'p': the callback that filters the element eligible for selection
    'f': the evaluation function that returns a value to be compared when
         applied on an element on x
    '_T': the type of the elements in x, for instance {IntVar}
    '_N': the type on which the minimum is computed, for instance {Integer}
    Returns the minimum element in x that satisfies the callback p or None
    if no element satisfies the callback.
    """
    sel = None
    for xi in x:
        if p(xi):
            if (sel is None) or (f(xi) - f(sel) < 0):
                sel = xi
    return sel


def first_fail(x: "list[int_var.IntVar]") -> "Callable[[], list[Callable[[], None]]]":
    """First-Fail strategy.
    It selects the first variable with a domain larger than one.
    Then it creates two branches. The left branch
    assigning the variable to its minimum value.
    The right branch removing this minimum value from the domain.
    'x': the list of variables on which the first fail strategy is applied.
    Returns a first-fail branching strategy.
    See factory make_dfs(Solver, Callable)
    """

    def call_back():
        xs = select_min(x, lambda xi: xi.size() > 1, lambda xi: xi.size())
        if xs is None:
            return _EMPTY
        else:
            v = xs.min()
            left = lambda: xs.get_solver().post(factory.equal(xs, v))
            right = lambda: xs.get_solver().post(factory.not_equal(xs, v=v))
            return [left, right]

    return call_back


def And(
    choices: "list[Callable[[], list[Callable[[], None]]]]",
) -> "Callable[[], list[Callable[[], None]]]":
    """Sequential Search combinator that linearly
    considers a list of branching generator.
    One branching of this list is executed
    when all the previous ones are exhausted (they return an empty array).
    'choices': the branching schemes considered sequentially in the sequential
    by path in the search tree
    Returns a branching scheme implementing the sequential search.
    See Sequencer
    """
    return search.Sequencer(choices)


def limited_discrepancy(
    branching: "Callable[[], list[Callable[[], None]]]", max_discrepancy: "int"
) -> "Callable[[], list[Callable[[], None]]]":
    """Limited Discrepancy Search combinator
    that limits the number of right decisions
    'branching': a branching scheme
    'max_discrepancy': a discrepancy limit (non-negative number)
    Returns a branch scheme that cuts off any path accumulating a
    discrepancy beyond the limit max_discrepancy.
    See LimitedDiscrepancyBranching
    """
    return search.LimitedDiscrepancyBranching(branching, max_discrepancy)


def last_conflict(
    variable_selector: "Callable[[], int_var.IntVar]",
    value_selector: "Callable[[int_var.IntVar], int]",
) -> "Callable[[], list[Callable[[], None]]]":
    """Last conflict heuristic
    Attempts to branch first on the last variable that caused an Inconsistency

    Lecoutre, C., Saïs, L., Tabary, S.,  Vidal, V. (2009).
    Reasoning from last conflict (s) in constraint programming.
    Artificial Intelligence, 173(18), 1592-1614.
    'variable_selector': returns the next variable to fix
    'value_selector': given a variable, returns the value to which it
    must be assigned on the left branch (and excluded on the right)
    """
    raise NotImplementedError("last_conflict")


def conflict_ordering_search(
    variable_selector: "Callable[[], int_var.IntVar]",
    value_selector: "Callable[[int_var.IntVar], int]",
) -> "Callable[[], list[Callable[[], None]]]":
    """Conflict Ordering Search

    Gay, S., Hartert, R., Lecoutre, C.,  Schaus, P. (2015).
    Conflict ordering search for scheduling problems.
    In International conference on principles and practice of constraint programming (pp. 140-148).
    Springer.
    'variable_selector': returns the next variable to fix
    'value_selector': given a variable, returns the value to which it
    must be assigned on the left branch (and excluded on the right)
    """
    raise NotImplementedError("conflict_ordering_search")
