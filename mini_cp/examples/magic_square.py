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

# The Magic Square problem.
# http://csplib.org/Problems/prob019/


def magic_square() -> "None":
    def solution_callback() -> "None":
        for i in range(n):
            print(",".join([str(xij) for xij in x[i]]))

    n = 6
    sum_result = int(n * (n * n + 1) / 2)

    cp = factory.make_solver()
    x = []
    for i in range(n):
        x.append([])
        for j in range(n):
            x[i].append(factory.make_int_var(cp, 1, n * n))

    x_flat = [x[i][j] for i in range(n) for j in range(n)]

    # AllDifferent
    cp.post(factory.all_different(x_flat))

    # Sum on lines
    for i in range(n):
        cp.post(factory.Sum(x[i], v=sum_result))

    # Sum on columns
    for j in range(len(x)):
        column = []
        for i in range(len(x)):
            column.append(x[i][j])
        cp.post(factory.Sum(column, v=sum_result))

    # Sum on diagonals
    diagonal_left = []
    diagonal_right = []
    for i in range(len(x)):
        diagonal_left.append(x[i][i])
        diagonal_right.append(x[n - i - 1][i])

    cp.post(factory.Sum(diagonal_left, v=sum_result))
    cp.post(factory.Sum(diagonal_right, v=sum_result))

    dfs = factory.make_dfs(cp, branching_scheme.first_fail(x_flat))

    dfs.on_solution(solution_callback)
    stats = dfs.solve(lambda stat: stat.number_of_solutions() >= 1)
    print(stats)


if __name__ == "__main__":
    magic_square()
