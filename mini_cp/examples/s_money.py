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

from mini_cp.cp import branching_scheme, factory

#  The Send-More-Money problem.
#     S E N D
#  +  M O R E
#  ----------
#   M O N E Y
#  All digits values are different.
#  Leading digits can't be zero


_S = 0
_E = 1
_N = 2
_D = 3
_M = 4
_O = 5
_R = 6
_Y = 7


def s_money() -> "None":
    cp = factory.make_solver(False)
    values = factory.make_int_var_array(cp, _Y + 1, min=0, max=9)
    carry = factory.make_int_var_array(cp, 4, min=0, max=1)

    cp.post(factory.all_different(values))
    cp.post(factory.not_equal(values[_S], v=0))
    cp.post(factory.not_equal(values[_M], v=0))
    cp.post(factory.equal(values[_M], y=carry[3]))
    cp.post(
        factory.equal(
            factory.sum_var(
                [
                    carry[2],
                    values[_S],
                    values[_M],
                    factory.minus(values[_O]),
                    factory.mul(carry[3], -10),
                ]
            ),
            0,
        )
    )
    cp.post(
        factory.equal(
            factory.sum_var(
                [
                    carry[1],
                    values[_E],
                    values[_O],
                    factory.minus(values[_N]),
                    factory.mul(carry[2], -10),
                ]
            ),
            0,
        )
    )
    cp.post(
        factory.equal(
            factory.sum_var(
                [
                    carry[0],
                    values[_N],
                    values[_R],
                    factory.minus(values[_E]),
                    factory.mul(carry[1], -10),
                ]
            ),
            0,
        )
    )
    cp.post(
        factory.equal(
            factory.sum_var(
                [
                    values[_D],
                    values[_E],
                    factory.minus(values[_Y]),
                    factory.mul(carry[0], -10),
                ]
            ),
            0,
        )
    )

    search = factory.make_dfs(cp, branching_scheme.first_fail(values))
    search.on_solution(
        lambda: print(f"Solution: {', '.join([str(v) for v in values])}")
    )
    stats = search.solve()
    print(f"#Solutions: {stats.number_of_solutions()}\n")
    print(f"Statistics: {stats}\n")


if __name__ == "__main__":
    s_money()
