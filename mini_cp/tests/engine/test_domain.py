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

import pytest

from mini_cp.engine import domain, solver, state


class MyDomainListener(domain.DomainListener):

    def __init__(self):
        self.n_fix = 0
        self.n_change = 0
        self.n_remove_below = 0
        self.n_remove_above = 0

    def empty(self) -> "None":
        pass

    def fix(self) -> "None":
        self.n_fix += 1

    def change(self) -> "None":
        self.n_change += 1

    def change_min(self) -> "None":
        self.n_remove_below += 1

    def change_max(self) -> "None":
        self.n_remove_above += 1


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_domain1(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    d_listener = MyDomainListener()
    dom = domain.SparseSetDomain(cp.get_state_manager(), 5, 10)

    dom.remove_above(8, d_listener)
    assert d_listener.n_change == 1
    assert d_listener.n_fix == 0
    assert d_listener.n_remove_above == 1
    assert d_listener.n_remove_below == 0

    dom.remove(6, d_listener)
    assert d_listener.n_change == 2
    assert d_listener.n_fix == 0
    assert d_listener.n_remove_above == 1
    assert d_listener.n_remove_below == 0

    dom.remove(5, d_listener)
    assert d_listener.n_change == 3
    assert d_listener.n_fix == 0
    assert d_listener.n_remove_above == 1
    assert d_listener.n_remove_below == 1

    dom.remove(7, d_listener)
    assert d_listener.n_change == 4
    assert d_listener.n_fix == 1
    assert d_listener.n_remove_above == 1
    assert d_listener.n_remove_below == 2


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_domain2(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    d_listener = MyDomainListener()
    dom = domain.SparseSetDomain(cp.get_state_manager(), 5, 10)

    dom.remove_all_but(7, d_listener)
    assert d_listener.n_change == 1
    assert d_listener.n_fix == 1
    assert d_listener.n_remove_above == 1
    assert d_listener.n_remove_below == 1


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_domain3(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    d_listener = MyDomainListener()
    dom = domain.SparseSetDomain(cp.get_state_manager(), 5, 10)

    dom.remove_above(5, d_listener)
    assert d_listener.n_change == 1
    assert d_listener.n_fix == 1
    assert d_listener.n_remove_above == 1
    assert d_listener.n_remove_below == 0
