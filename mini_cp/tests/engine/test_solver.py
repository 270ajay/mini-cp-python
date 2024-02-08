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


@pytest.mark.parametrize("by_copy", [False, True])
def test_solve_subject_to(by_copy: "bool") -> "None":
    cp = factory.make_solver(by_copy)
    x = factory.make_int_var_array(cp, 3, 2)

    dfs = factory.make_dfs(cp, branching_scheme.first_fail(x))

    stats1 = dfs.solve_subject_to(
        lambda l: False, lambda: cp.post(factory.equal(x[0], 0))
    )

    assert stats1.number_of_solutions() == 4

    stats2 = dfs.solve(lambda l: False)

    assert stats2.number_of_solutions() == 8


@pytest.mark.parametrize("by_copy", [False, True])
def test_dfs(by_copy: "bool") -> "None":

    def callback() -> "list[Callable[[], None]]":
        sel = -1
        for i in range(len(values)):
            if values[i].size() > 1 and sel == -1:
                sel = i
        if sel == -1:
            return []
        else:
            return [
                lambda: cp.post(factory.equal(values[sel], 0)),
                lambda: cp.post(factory.equal(values[sel], 1)),
            ]

    cp = factory.make_solver(by_copy)
    values = factory.make_int_var_array(cp, 3, 2)
    dfs = factory.make_dfs(cp, callback)
    stats = dfs.solve()

    assert stats.number_of_solutions() == 8
    assert stats.number_of_failures() == 0
    assert stats.number_of_nodes() == (8 + 4 + 2)
