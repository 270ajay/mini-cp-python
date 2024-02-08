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

from mini_cp.cp import factory
from mini_cp.engine import constraint, exceptions, int_var, solver, state


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_bool_var(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    b = factory.make_bool_var(cp)

    # 1 - b
    not_b = int_var.BoolVarImpl(
        int_var.IntVarViewOffset(int_var.IntVarViewOpposite(b), 1)
    )

    assert b.is_fixed() is False
    assert not_b.is_fixed() is False

    b.fix(False)
    assert b.is_false() is True
    assert not_b.is_true() is True


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_var(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    x = factory.make_int_var(cp, sz=10)
    y = factory.make_int_var(cp, sz=10)

    cp.get_state_manager().save_state()

    try:
        assert x.is_fixed() is False
        x.remove(5)
        assert x.size() == 9
        x.fix(7)
        assert x.size() == 1
        assert x.min() == 7
        assert x.max() == 7
    except exceptions.InconsistencyException:
        assert False  # should not fail here

    try:
        x.fix(8)
        assert False  # should have failed
    except exceptions.InconsistencyException:
        pass

    cp.get_state_manager().restore_state()
    cp.get_state_manager().save_state()

    assert x.is_fixed() is False
    assert x.size() == 10

    for i in range(10):
        assert x.contains(i)

    assert x.contains(-1) is False


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_on_domain_change_on_bind(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    propagate_called = [False]

    def callback() -> "None":
        propagate_called[0] = True

    x = factory.make_int_var(cp, sz=10)
    y = factory.make_int_var(cp, sz=10)

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.when_fixed(callback)
            y.when_domain_change(callback)

    try:
        cp.post(AConstraint(cp))
        x.remove(8)
        cp.fix_point()
        assert propagate_called[0] is False
        x.fix(4)
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False
        y.remove(10)
        cp.fix_point()
        assert propagate_called[0] is False
        y.remove(9)
        cp.fix_point()
        assert propagate_called[0] is True
    except exceptions.InconsistencyException:
        assert False  # Should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_arbitrary_range_domains(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    x = factory.make_int_var(cp, -10, 10)
    cp.get_state_manager().save_state()

    try:
        assert x.is_fixed() is False
        x.remove(-9)
        x.remove(-10)

        assert x.size() == 19
        x.fix(-4)
        assert x.size() == 1
        assert x.is_fixed() is True
        assert x.min() == -4
    except exceptions.InconsistencyException:
        assert False  # Should not fail here

    try:
        x.fix(8)
        assert False  # Should fail here
    except exceptions.InconsistencyException:
        pass

    cp.get_state_manager().restore_state()

    assert x.size() == 21
    for i in range(-10, 10):
        assert x.contains(i) is True
    assert x.contains(-11) is False


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_arbitrary_set_domains(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    try:
        dom: "set[int]" = {-7, -10, 6, 9, 10, 12}
        x = factory.make_int_var(cp, values=dom)
        assert cp == x.get_solver()
        cp.get_state_manager().save_state()

        try:
            for i in range(-15, 15):
                if i in dom:
                    assert x.contains(i) is True
                else:
                    assert x.contains(i) is False
            x.fix(-7)
        except exceptions.InconsistencyException:
            assert False  # Should not fail here

        try:
            x.fix(-10)
            assert False  # Should fail here
        except exceptions.InconsistencyException:
            pass

        cp.get_state_manager().restore_state()
        for i in range(-15, 15):
            if i in dom:
                assert x.contains(i) is True
            else:
                assert x.contains(i) is False
        assert x.size() == 6

    except NotImplementedError:
        pass


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_on_bound_change(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    x = factory.make_int_var(cp, sz=10)
    y = factory.make_int_var(cp, sz=10)
    propagate_called = [False]

    def callback() -> "None":
        propagate_called[0] = True

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.when_fixed(callback)
            y.when_domain_change(callback)

    try:
        cp.post(AConstraint(cp))
        x.remove(8)
        cp.fix_point()
        assert propagate_called[0] is False
        x.remove(9)
        cp.fix_point()
        assert propagate_called[0] is False
        x.fix(4)
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False
        assert y.contains(10) is False
        y.remove(10)
        cp.fix_point()
        assert propagate_called[0] is False
        propagate_called[0] = False
        y.remove(2)
        cp.fix_point()
        assert propagate_called[0] is True

    except exceptions.InconsistencyException:
        assert False  # Should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_remove_above(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    x = factory.make_int_var(cp, sz=10)
    propagate_called = [False]

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.propagate_on_bound_change(self)

        def propagate(self) -> "None":
            propagate_called[0] = True

    try:
        cp.post(AConstraint(cp))
        x.remove(8)
        cp.fix_point()
        assert propagate_called[0] is False
        x.remove_above(8)
        assert x.max() == 7
        cp.fix_point()
        assert propagate_called[0] is True
    except exceptions.InconsistencyException:
        assert False  # Should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_remove_below(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    x = factory.make_int_var(cp, sz=10)
    propagate_called = [False]

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.propagate_on_bound_change(self)

        def propagate(self) -> "None":
            propagate_called[0] = True

    try:
        cp.post(AConstraint(cp))
        x.remove(3)
        cp.fix_point()
        assert propagate_called[0] is False
        x.remove_below(3)
        assert x.min() == 4
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False

        x.remove_below(5)
        assert x.min() == 5
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False

    except exceptions.InconsistencyException:
        assert False  # Should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_fill_array(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    x = factory.make_int_var(cp, 2, 9)
    x.remove(3)
    x.remove(5)
    x.remove(2)
    x.remove(9)

    values: "list[int]" = [0] * 10
    s = x.fill_array(values)
    dom = set()
    for i in range(s):
        dom.add(values[i])
    expected_dom: "set[int]" = {4, 6, 7, 8}
    assert dom == expected_dom


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_arbitrary_set_domains_max_int(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    try:
        dom: "set[int]" = {2147483647}
        var1 = factory.make_int_var(cp, values=dom)
        assert var1.max() == 2147483647
    except NotImplementedError:
        pass
    except MemoryError:
        assert False, (
            "You created an array to big. Look at valid min and "
            "max values for constructing your StateSparseSet"
        )


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_mult_var(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    # domain is {-9, -6, -3, 0, 3, 6, 9, 12}
    x = factory.mul(factory.mul(factory.make_int_var(cp, -3, 4), -3), -1)
    assert x.min() == -9
    assert x.max() == 12
    assert x.size() == 8
    cp.get_state_manager().save_state()

    try:
        assert x.is_fixed() is False
        x.remove(-6)
        assert x.contains(-6) is False
        x.remove(2)
        assert x.contains(0) is True
        assert x.contains(3) is True
        assert x.size() == 7
        x.remove_above(7)
        assert x.max() == 6
        x.remove_below(-8)
        assert x.min() == -3
        x.fix(3)
        assert x.is_fixed() is True
        assert x.max() == 3
    except exceptions.InconsistencyException:
        assert False  # should not fail here

    try:
        x.fix(8)
        assert False  # should fail here
    except exceptions.InconsistencyException:
        pass

    cp.get_state_manager().restore_state()
    assert x.size() == 8
    assert x.contains(-1) is False


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_mult_var_on_domain_change_on_bind(
    state_manager: "state.StateManager",
) -> "None":
    cp = solver.MiniCP(state_manager)
    propagate_called = [False]

    x = factory.mul(factory.make_int_var(cp, sz=10), 1)
    y = factory.mul(factory.make_int_var(cp, sz=10), 1)

    def callback() -> "None":
        propagate_called[0] = True

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.when_fixed(callback)
            y.when_domain_change(callback)

    try:
        cp.post(AConstraint(cp))
        x.remove(8)
        cp.fix_point()
        assert propagate_called[0] is False
        x.fix(4)
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False
        y.remove(10)
        cp.fix_point()
        assert propagate_called[0] is False
        y.remove(9)
        cp.fix_point()
        assert propagate_called[0] is True
    except exceptions.InconsistencyException:
        assert False  # should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_mult_var_on_bound_change(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    propagate_called = [False]

    x = factory.mul(factory.make_int_var(cp, sz=10), 1)
    y = factory.mul(factory.make_int_var(cp, sz=10), 1)

    def callback() -> "None":
        propagate_called[0] = True

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.when_fixed(callback)
            y.when_domain_change(callback)

    try:
        cp.post(AConstraint(cp))
        x.remove(8)
        cp.fix_point()
        assert propagate_called[0] is False
        x.remove(9)
        cp.fix_point()
        assert propagate_called[0] is False
        x.fix(4)
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False
        assert y.contains(10) is False
        y.remove(10)
        cp.fix_point()
        assert propagate_called[0] is False
        y.remove(2)
        cp.fix_point()
        assert propagate_called[0] is True
    except exceptions.InconsistencyException:
        assert False  # should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_mult_var_over_flow(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    try:
        factory.mul(factory.make_int_var(cp, 1000000, 1000000), 10000000)
        assert False  # Should fail
    except OverflowError:
        pass


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_offset_var(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)

    # Domain is {0,1,2,3,4,5,6,7}
    x = factory.plus(factory.make_int_var(cp, -3, 4), 3)

    assert x.min() == 0
    assert x.max() == 7
    assert x.size() == 8

    cp.get_state_manager().save_state()

    try:
        assert x.is_fixed() is False
        x.remove(0)
        assert x.contains(0) is False
        x.remove(3)
        assert x.contains(1) is True
        assert x.contains(2) is True
        x.remove_above(6)
        assert x.max() == 6
        x.remove_below(3)
        assert x.min() == 4
        x.fix(5)
        assert x.is_fixed() is True
        assert x.max() == 5
    except exceptions.InconsistencyException:
        assert False  # should not fail here

    try:
        x.fix(4)
        assert False  # should have failed
    except exceptions.InconsistencyException:
        pass

    cp.get_state_manager().restore_state()
    assert x.size() == 8
    assert x.contains(-1) is False


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_offset_var_on_domain_change_on_fix(
    state_manager: "state.StateManager",
) -> "None":
    cp = solver.MiniCP(state_manager)
    propagate_called = [False]

    x = factory.plus(factory.make_int_var(cp, sz=10), 1)  # 1..11
    y = factory.plus(factory.make_int_var(cp, sz=10), 1)  # 1..11

    def callback() -> "None":
        propagate_called[0] = True

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.when_fixed(callback)
            y.when_domain_change(callback)

    try:
        cp.post(AConstraint(cp))
        x.remove(9)
        cp.fix_point()
        assert propagate_called[0] is False
        x.fix(5)
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False
        y.remove(11)
        cp.fix_point()
        assert propagate_called[0] is False
        y.remove(10)
        cp.fix_point()
        assert propagate_called[0] is True
    except exceptions.InconsistencyException:
        assert False  # should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_offset_var_on_bound_change(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    propagate_called = [False]

    x = factory.plus(factory.make_int_var(cp, sz=10), 1)  # 1..11
    y = factory.plus(factory.make_int_var(cp, sz=10), 1)  # 1..11

    def callback() -> "None":
        propagate_called[0] = True

    class AConstraint(constraint.AbstractConstraint):
        def __init__(self, cp: "solver.Solver"):
            super().__init__(cp)

        def post(self) -> "None":
            x.when_fixed(callback)
            y.when_domain_change(callback)

    try:
        cp.post(AConstraint(cp))
        x.remove(9)
        cp.fix_point()
        assert propagate_called[0] is False
        x.remove(10)
        cp.fix_point()
        assert propagate_called[0] is False
        x.fix(5)
        cp.fix_point()
        assert propagate_called[0] is True
        propagate_called[0] = False
        assert y.contains(11) is False
        y.remove(11)
        cp.fix_point()
        assert propagate_called[0] is False
        y.remove(3)
        cp.fix_point()
        assert propagate_called[0] is True
    except exceptions.InconsistencyException:
        assert False  # should not fail


@pytest.mark.parametrize("state_manager", [state.Trailer(), state.Copier()])
def test_int_offset_var_over_flow(state_manager: "state.StateManager") -> "None":
    cp = solver.MiniCP(state_manager)
    try:
        factory.plus(factory.make_int_var(cp, 2147483647 - 5, 2147483647 - 2), 3)
        assert False  # Should fail
    except OverflowError:
        pass
