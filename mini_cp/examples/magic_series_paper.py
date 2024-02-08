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

# The Magic Series problem.
# http://csplib.org/Problems/prob019/


def magic_series_paper() -> "None":
    def branching_callback() -> "list[Callable[[], None]]":
        idx = -1  # index of the first variable that is not fixed
        for k in range(len(s)):
            if s[k].size() > 1:
                idx = k
                break
        if idx == -1:
            return []
        else:
            si = s[idx]
            v = si.min()
            return [
                lambda: cp.post(factory.equal(si, v)),
                lambda: cp.post(factory.not_equal(si, v=v)),
            ]

    n = 8
    cp = factory.make_solver(False)
    s = factory.make_int_var_array(cp, n, n)

    for i in range(n):
        fi = i
        cp.post(
            factory.Sum(
                factory.make_int_var_array(
                    cp, n, body=lambda j: factory.is_equal(s[j], fi)
                ),
                s[i],
            )
        )

    cp.post(factory.Sum(s, v=n))
    cp.post(
        factory.Sum(
            factory.make_int_var_array(cp, n, body=lambda i: factory.mul(s[i], i)), v=n
        )
    )

    dfs = factory.make_dfs(cp, branching_callback)
    dfs.on_solution(lambda: print(f"Solution: {', '.join([str(si) for si in s])}"))
    stats = dfs.solve()
    print(stats)


if __name__ == "__main__":
    magic_series_paper()
