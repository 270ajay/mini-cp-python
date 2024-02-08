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
from mini_cp.engine import int_var


def bin_packing() -> "None":

    def branching_callback() -> "list[Callable[[], None]]":
        item = _first_index_not_bound(x)
        if item == -1:
            return []
        else:
            # Get the maximum value among the fixed variables of x
            fixed_values = [xi.min() for xi in x if xi.is_fixed()]
            max_used_bin = -1
            if fixed_values:
                max_used_bin = max(fixed_values)

            branches = []
            # dynamic symmetry breaking: branch on at most one empty bin
            for j in range(0, min(max_used_bin + 1, n_bins - 1) + 1):
                if x[item].contains(j):
                    bin = j
                    branches.append(lambda: cp.post(factory.equal(x[item], bin)))
            return branches

    def solution_callback() -> "None":
        print(f"--- {_first_index_not_bound(x)}")
        print(",".join([str(xi) for xi in x]))
        print(",".join([str(li) for li in l]))

    capa = 9
    items = [2, 2, 2, 2, 4, 4, 5, 5, 5, 6, 7]
    n_bins = 5
    n_items = len(items)

    cp = factory.make_solver()
    x = factory.make_int_var_array(cp, n_items, n_bins)
    l = factory.make_int_var_array(cp, n_bins, capa + 1)

    # in_bin[j][i] = 1 if item i is placed in bin j
    in_bin = []
    for j in range(n_bins):
        in_bin.append([])
        for i in range(n_items):
            in_bin[j].append(factory.is_equal(x[i], j))

    # Bin packing constraint
    for j in range(n_bins):
        wj = []
        for i in range(n_items):
            wj.append(factory.mul(in_bin[j][i], items[i]))
        cp.post(factory.Sum(wj, l[j]))

    # Redundant constraint: sum of bin load = sum of item weights
    cp.post(factory.Sum(l, v=sum(items)))

    # Break symmetries imposing increasing loads
    # for j in range(n_bins - 1):
    #     cp.post(factory.less_or_equal(l[j], y=l[j+1]))

    dfs = factory.make_dfs(cp, branching_callback)
    dfs.on_solution(solution_callback)
    stats = dfs.solve(lambda s: s.number_of_solutions() >= 1)
    print(stats)


def _first_index_not_bound(x: "list[int_var.IntVar]") -> "int":
    """Returns the first unfixed variable of x"""
    item = -1
    for i in range(len(x)):
        if x[i].size() > 1:
            item = i
            break
    return item


if __name__ == "__main__":
    bin_packing()
