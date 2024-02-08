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

#  The Quadratic Assignment problem.
#  There are a set of n facilities and a set of n locations.
#  For each pair of locations, a distance is specified and for
#  each pair of facilities a weight or flow is specified
#  (e.g., the amount of supplies transported between the two facilities).
#  The problem is to assign all facilities to different locations
#  with the goal of minimizing the sum of the distances multiplied
#  by the corresponding flows.
#  https://en.wikipedia.org/wiki/Quadratic_assignment_problem


def qap_paper() -> "None":
    def branching_callback() -> "list[Callable[[], None]]":
        idx = -1  # index of the first variable that is not fixed
        for l in range(0, len(x)):
            if x[l].size() > 1:
                idx = l
                break
        if idx == -1:
            return []
        else:
            xi = x[idx]
            v = xi.min()
            return [
                lambda: cp.post(factory.equal(xi, v)),
                lambda: cp.post(factory.not_equal(xi, v=v)),
            ]

    n = 12
    # Weights
    w = [
        [0, 90, 10, 23, 43, 0, 0, 0, 0, 0, 0, 0],
        [90, 0, 0, 0, 0, 88, 0, 0, 0, 0, 0, 0],
        [10, 0, 0, 0, 0, 0, 26, 16, 0, 0, 0, 0],
        [23, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [43, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 88, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 26, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 16, 0, 0, 0, 0, 0, 0, 96, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 29, 0],
        [0, 0, 0, 0, 0, 0, 0, 96, 0, 0, 0, 37],
        [0, 0, 0, 0, 0, 0, 0, 0, 29, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 37, 0, 0],
    ]
    # Distances
    d = [
        [0, 36, 54, 26, 59, 72, 9, 34, 79, 17, 46, 95],
        [36, 0, 73, 35, 90, 58, 30, 78, 35, 44, 79, 36],
        [54, 73, 0, 21, 10, 97, 58, 66, 69, 61, 54, 63],
        [26, 35, 21, 0, 93, 12, 46, 40, 37, 48, 68, 85],
        [59, 90, 10, 93, 0, 64, 5, 29, 76, 16, 5, 76],
        [72, 58, 97, 12, 64, 0, 96, 55, 38, 54, 0, 34],
        [9, 30, 58, 46, 5, 96, 0, 83, 35, 11, 56, 37],
        [34, 78, 66, 40, 29, 55, 83, 0, 44, 12, 15, 80],
        [79, 35, 69, 37, 76, 38, 35, 44, 0, 64, 39, 33],
        [17, 44, 61, 48, 16, 54, 11, 12, 64, 0, 70, 86],
        [46, 79, 54, 68, 5, 0, 56, 15, 39, 70, 0, 18],
        [95, 36, 63, 85, 76, 34, 37, 80, 33, 86, 18, 0],
    ]

    # Model creation and resolution
    cp = factory.make_solver()
    x = factory.make_int_var_array(cp, n, n)
    cp.post(factory.all_different(x))
    weighted_dist = []
    for i in range(n):
        for j in range(n):
            dij = factory.element_2d(d, x[i], x[j])
            weighted_dist.append(factory.mul(dij, w[i][j]))
    tot_cost = factory.sum_var(weighted_dist)
    obj = cp.minimize(tot_cost)

    dfs = factory.make_dfs(cp, branching_callback)
    dfs.on_solution(lambda: print(f"Objective: {tot_cost.min()}"))
    stats = dfs.optimize(obj)
    print(stats)


if __name__ == "__main__":
    qap_paper()
