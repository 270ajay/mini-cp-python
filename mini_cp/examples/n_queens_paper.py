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

from mini_cp.cp import factory

# The N-Queens problem.
# http://csplib.org/Problems/prob054/


def n_queens_paper() -> "None":
    def branching_callback() -> "list[Callable[[], None]]":
        idx = -1  # index of the first variable that is not fixed
        for k in range(len(q)):
            if q[k].size() > 1:
                idx = k
                break
        if idx == -1:
            return []
        else:
            qi = q[idx]
            v = qi.min()
            return [
                lambda: cp.post(factory.equal(qi, v)),
                lambda: cp.post(factory.not_equal(qi, v=v)),
            ]

    n = 12
    cp = factory.make_solver(False)
    q = factory.make_int_var_array(cp, n, n)

    for i in range(n):
        for j in range(i + 1, n):
            cp.post(factory.not_equal(q[i], q[j]))
            cp.post(factory.not_equal(q[i], q[j], j - i))
            cp.post(factory.not_equal(q[i], q[j], i - j))

    search = factory.make_dfs(cp, branching_callback)
    search.on_solution(lambda: print(f"Solution: {' '.join([str(qi) for qi in q])}"))
    stats = search.solve()
    print(stats)


if __name__ == "__main__":
    n_queens_paper()
