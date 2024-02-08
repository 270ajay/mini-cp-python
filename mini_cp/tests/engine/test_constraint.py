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
from mini_cp.engine import constraint, exceptions, int_var, solver

_MAX_VALUE = 2147483647
_MIN_VALUE = -2147483648


@pytest.mark.parametrize("by_copy", [False, True])
def test_not_equal(by_copy: "bool") -> "None":
    cp = factory.make_solver(by_copy)
    x = factory.make_int_var(cp, sz=10)
    y = factory.make_int_var(cp, sz=10)
    try:
        cp.post(factory.not_equal(x, y))
        cp.post(factory.equal(x, 6))
        assert y.contains(6) is False
        assert y.size() == 9
    except exceptions.InconsistencyException:
        assert False  # should not fail
    assert y.contains(6) is False


class TestAbsolute:

    @pytest.mark.parametrize("by_copy", [False, True])
    def test0(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -5, 5)
            y = factory.make_int_var(cp, -10, 10)
            cp.post(constraint.Absolute(x, y))

            assert y.min() == 0
            assert y.max() == 5
            assert x.size() == 11
            x.remove_above(-2)
            cp.fix_point()
            assert y.min() == 2
            x.remove_below(-4)
            cp.fix_point()
            assert y.max() == 4
        except exceptions.InconsistencyException:
            assert False  # should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test1(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -5, 5)
            y = factory.make_int_var(cp, -10, 10)
            cp.post(factory.not_equal(x, v=0))
            cp.post(factory.not_equal(x, v=5))
            cp.post(factory.not_equal(x, v=-5))
            cp.post(constraint.Absolute(x, y))

            assert y.min() == 1
            assert y.max() == 4
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test2(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -5, 0)
            y = factory.make_int_var(cp, 4, 4)
            cp.post(constraint.Absolute(x, y))
            assert x.is_fixed() is True
            assert y.is_fixed() is True
            assert x.max() == -4
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test3(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, 7, 7)
            y = factory.make_int_var(cp, -1000, 12)
            cp.post(constraint.Absolute(x, y))
            assert x.is_fixed() is True
            assert y.is_fixed() is True
            assert y.max() == 7
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test4(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -5, 10)
            y = factory.make_int_var(cp, -6, 7)
            cp.post(constraint.Absolute(x, y))
            assert x.max() == 7
            assert x.min() == -5

            cp.post(factory.not_equal(y, v=0))
            cp.post(factory.less_or_equal(x, 4))
            assert y.max() == 5
            cp.post(factory.less_or_equal(x, -2))
            assert y.min() == 2

            y.remove_below(5)
            cp.fix_point()
            assert x.is_fixed() is True
            assert y.is_fixed() is True
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass


@pytest.mark.parametrize("by_copy", [False, True])
def test_maximize(by_copy: "bool") -> "None":
    def callback() -> "list[Callable[[], None]]":
        if y.is_fixed():
            return []
        else:
            return [
                lambda: cp.post(factory.equal(y, y.min())),
                lambda: cp.post(factory.not_equal(y, v=y.min())),
            ]

    try:
        cp = factory.make_solver(by_copy)
        y = factory.make_int_var(cp, 10, 20)
        x = [y]
        dfs = factory.make_dfs(cp, callback)
        stats = dfs.solve()
        assert stats.number_of_solutions() == 11
    except exceptions.InconsistencyException:
        assert False  # Should not fail


class TestMaximum:

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_1(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var_array(cp, 3, 10)
            y = factory.make_int_var(cp, -5, 20)
            constraint.Maximum(x, y).post()

            # x[i] = 0..9
            # y = 0..9
            assert y.max() == 9
            assert y.min() == 0
            y.remove_above(8)
            cp.fix_point()

            # x[i] = 0..8
            # y = 0..8
            assert x[0].max() == 8
            assert x[1].max() == 8
            assert x[2].max() == 8
            y.remove_below(5)
            x[0].remove_above(2)
            x[1].remove_below(6)
            x[2].remove_below(6)
            cp.fix_point()

            # x0 = 0..1
            # x1 = 6..8
            # x2 = 6..8
            # y = 6..8 (the maximum is either x1 or x2)
            assert y.max() == 8
            assert y.min() == 6
            y.remove_below(7)
            x[1].remove_above(6)

            # x0 = 0..2
            # x1 = 6
            # x2 = 6..8
            # y = 7..8
            cp.fix_point()  # propagate the maximum constraint
            assert (
                x[2].min() == 7
            ), "In some cases, y can also change the minimum value of one of the x's"
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_2(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x1 = factory.make_int_var(cp, 0, 0)
            x2 = factory.make_int_var(cp, 1, 1)
            x3 = factory.make_int_var(cp, 2, 2)
            y = factory.maximum([x1, x2, x3])
            assert y.max() == 2
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_3(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x1 = factory.make_int_var(cp, 0, 10)
            x2 = factory.make_int_var(cp, 0, 10)
            x3 = factory.make_int_var(cp, -5, 50)
            y = factory.maximum([x1, x2, x3])
            y.remove_above(5)
            cp.fix_point()
            assert x1.max() == 5
            assert x2.max() == 5
            assert x3.max() == 5
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_4(self, by_copy: "bool") -> "None":
        def callback() -> "None":
            max_val = max([xi.max() for xi in x])
            variables = "; ".join([f"x[{i}] = {x[i]}" for i in range(4)])
            assert (
                y.min() == max_val
            ), f"The variables are \n{variables}\nbut you set y to {y}"
            assert (
                y.max() == max_val
            ), f"The variables are \n{variables}\nbut you set y to {y}"
            assert (
                y.is_fixed() is True
            ), "If all the x[i]'s are fixed, y should be fixed as well"

        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var_array(cp, 4, 5)
            y = factory.make_int_var(cp, -5, 20)

            all_int_vars = [x[i] for i in range(len(x))]
            all_int_vars.append(y)
            dfs = factory.make_dfs(cp, branching_scheme.first_fail(all_int_vars))
            cp.post(constraint.Maximum(x, y))
            # 5*5*5*5 # 625
            dfs.on_solution(callback)
            stats = dfs.solve()
            assert stats.number_of_solutions() == 625
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_5(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var_array(cp, 3, 10)
            y = factory.make_int_var(cp, -5, 20)
            constraint.Maximum(x, y).post()

            assert y.max() == 9
            assert y.min() == 0
            x[0].remove_above(3)
            y.remove_below(6)
            cp.fix_point()
            assert y.min() == 6
            assert y.max() == 9
            assert x[1].min() == 0
            assert x[2].min() == 0
        except NotImplementedError:
            pass

    # TODO: add remaining tests


class TestEqual:

    def _equal_dom(self, x: "int_var.IntVar", y: "int_var.IntVar") -> "bool":
        for v in range(x.min(), x.max()):
            if x.contains(v) and not y.contains(v):
                return False
        for v in range(y.min(), y.max()):
            if y.contains(v) and not x.contains(v):
                return False

        return True

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_equal1(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, 0, 10)
            y = factory.make_int_var(cp, 0, 10)
            cp.post(factory.equal(x, y=y))
            x.remove_above(7)
            cp.fix_point()
            assert self._equal_dom(x, y)
            y.remove_above(6)
            cp.fix_point()
            x.remove(3)
            cp.fix_point()
            assert self._equal_dom(x, y)
            x.fix(1)
            cp.fix_point()
            assert self._equal_dom(x, y)
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_equal2(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, _MAX_VALUE - 20, _MAX_VALUE - 1)
            y = factory.make_int_var(cp, _MAX_VALUE - 10, _MAX_VALUE - 1)
            cp.post(factory.not_equal(x, v=_MAX_VALUE - 5))
            cp.post(factory.equal(x, y=y))
            cp.post(factory.equal(x, v=_MAX_VALUE - 1))
            assert y.min() == _MAX_VALUE - 1
        except exceptions.InconsistencyException:
            assert False  # Should not fail


class TestLessOrEqual:

    @pytest.mark.parametrize("by_copy", [False, True])
    def test0(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -5, 5)
            y = factory.make_int_var(cp, -10, 10)
            cp.post(constraint.LessOrEqual(x, y))
            assert y.min() == -5
            y.remove_above(3)
            cp.fix_point()
            assert x.size() == 9
            assert x.max() == 3
            x.remove_below(-4)
            cp.fix_point()
            assert y.min() == -4
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass


class TestIsEqual:

    @pytest.mark.parametrize("by_copy", [False, True])
    def test1(self, by_copy: "bool") -> "None":

        def callback() -> "None":
            assert x.min() == -2
            assert b.is_true() is True

        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            b = factory.is_equal(x, -2)
            search = factory.make_dfs(cp, branching_scheme.first_fail([x]))
            stats = search.solve()
            search.on_solution(callback)
            assert stats.number_of_solutions() == 12
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test2(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            b = factory.is_equal(x, -2)

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 1))
            assert x.min() == -2
            cp.get_state_manager().restore_state()

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 0))
            assert x.contains(-2) is False
            cp.get_state_manager().restore_state()
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test3(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            cp.post(factory.equal(x, -2))

            b = factory.make_bool_var(cp)
            cp.post(constraint.IsEqual(b, x, -2))
            assert b.is_true() is True

            b = factory.make_bool_var(cp)
            cp.post(constraint.IsEqual(b, x, -3))
            assert b.is_false() is True

        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test4(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            b = factory.make_bool_var(cp)

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 1))
            cp.post(constraint.IsEqual(b, x, -2))
            assert x.min() == -2
            cp.get_state_manager().restore_state()

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 0))
            cp.post(constraint.IsEqual(b, x, -2))
            assert x.contains(-2) is False
            cp.get_state_manager().restore_state()
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass


class TestIsLessOrEqual:

    @pytest.mark.parametrize("by_copy", [False, True])
    def test1(self, by_copy: "bool") -> "None":
        def callback() -> "None":
            assert x.min() <= 3 and b.is_true() or x.min() > 3 and b.is_false()

        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            b = factory.make_bool_var(cp)
            cp.post(constraint.IsLessOrEqual(b, x, 3))
            search = factory.make_dfs(cp, branching_scheme.first_fail([x]))
            search.on_solution(callback)
            stats = search.solve()
            assert stats.number_of_solutions() == 12
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test2(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            b = factory.make_bool_var(cp)
            cp.post(constraint.IsLessOrEqual(b, x, -2))

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 1))
            assert x.max() == -2
            cp.get_state_manager().restore_state()

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 0))
            assert x.min() == -1
            cp.get_state_manager().restore_state()
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test3(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            cp.post(factory.equal(x, -2))

            b = factory.make_bool_var(cp)
            cp.post(constraint.IsLessOrEqual(b, x, -2))
            assert b.is_true() is True

            b = factory.make_bool_var(cp)
            cp.post(constraint.IsLessOrEqual(b, x, -3))
            assert b.is_false() is True
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test4(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -4, 7)
            b = factory.make_bool_var(cp)

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 1))
            cp.post(constraint.IsLessOrEqual(b, x, -2))
            assert x.max() == -2
            cp.get_state_manager().restore_state()

            cp.get_state_manager().save_state()
            cp.post(factory.equal(b, 0))
            cp.post(constraint.IsLessOrEqual(b, x, -2))
            assert x.min() == -1
            cp.get_state_manager().restore_state()
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test5(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -5, 10)
            b = factory.make_bool_var(cp)

            cp.get_state_manager().save_state()
            cp.post(constraint.IsLessOrEqual(b, x, -6))
            assert b.is_fixed() is True
            assert b.is_false() is True
            cp.get_state_manager().restore_state()

            cp.get_state_manager().save_state()
            cp.post(constraint.IsLessOrEqual(b, x, 11))
            assert b.is_fixed() is True
            assert b.is_true() is True
            cp.get_state_manager().restore_state()
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test6(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -5, -3)
            b = factory.make_bool_var(cp)
            cp.get_state_manager().save_state()
            cp.post(constraint.IsLessOrEqual(b, x, -3))
            assert b.is_true() is True
            cp.get_state_manager().restore_state()
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass


class TestElement1D:
    # TODO
    pass


class TestElement2D:

    @pytest.mark.parametrize("by_copy", [False, True])
    def test1(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -2, 40)
            y = factory.make_int_var(cp, -3, 10)
            z = factory.make_int_var(cp, 2, 40)
            T = [[9, 8, 7, 5, 6], [9, 1, 5, 2, 8], [8, 3, 1, 4, 9], [9, 1, 2, 8, 6]]

            cp.post(constraint.Element2D(T, x, y, z))
            assert x.min() == 0
            assert y.min() == 0
            assert x.max() == 3
            assert y.max() == 4
            assert z.min() == 2
            assert z.max() == 9
            z.remove_above(7)
            cp.fix_point()
            assert y.min() == 1
            x.remove(0)
            cp.fix_point()
            assert z.max() == 6
            assert x.max() == 3
            y.remove(4)
            cp.fix_point()
            assert z.max() == 5
            assert z.min() == 2
            y.remove(2)
            cp.fix_point()
            assert z.max() == 4
            assert z.min() == 2
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test2(self, by_copy: "bool") -> "None":
        def callback() -> "None":
            assert T[x.min()][y.min()] == z.min()

        try:
            cp = factory.make_solver(by_copy)
            x = factory.make_int_var(cp, -2, 40)
            y = factory.make_int_var(cp, -3, 10)
            z = factory.make_int_var(cp, -20, 40)
            T = [
                [3, 2, 1, -1, 0],
                [3, -5, -1, -4, 2],
                [2, -3, -5, -2, 3],
                [3, -5, -4, 2, 0],
            ]

            cp.post(constraint.Element2D(T, x, y, z))
            dfs = factory.make_dfs(cp, branching_scheme.first_fail([x, y, z]))
            dfs.on_solution(callback)
            stats = dfs.solve()
            assert stats.number_of_solutions() == 20
        except exceptions.InconsistencyException:
            assert False  # Should not fail


class TestSum:

    @pytest.mark.parametrize("by_copy", [False, True])
    def test1(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            y = factory.make_int_var(cp, -100, 100)
            x = [
                factory.make_int_var(cp, 0, 5),
                factory.make_int_var(cp, 1, 5),
                factory.make_int_var(cp, 0, 5),
            ]
            cp.post(constraint.Sum(x, y))
            assert y.min() == 1
            assert y.max() == 15
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test2(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = [
                factory.make_int_var(cp, -5, 5),
                factory.make_int_var(cp, 1, 2),
                factory.make_int_var(cp, 0, 1),
            ]
            y = factory.make_int_var(cp, 0, 100)
            cp.post(constraint.Sum(x, y))
            assert x[0].min() == -3
            assert y.min() == 0
            assert y.max() == 8
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test3(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = [
                factory.make_int_var(cp, -5, 5),
                factory.make_int_var(cp, 1, 2),
                factory.make_int_var(cp, 0, 1),
            ]
            y = factory.make_int_var(cp, 5, 5)
            cp.post(constraint.Sum(x, y))
            x[0].remove_below(1)
            # 1-5 + 1-2 + 0-1 = 5
            x[1].fix(1)
            # 1.5 + 1 + 0-1 = 5
            cp.fix_point()
            assert x[0].max() == 4
            assert x[0].min() == 3
            assert x[2].max() == 1
            assert x[2].min() == 0
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test4(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = [
                factory.make_int_var(cp, 0, 5),
                factory.make_int_var(cp, 0, 2),
                factory.make_int_var(cp, 0, 1),
            ]
            cp.post(constraint.Sum(x, v=0))
            assert x[0].max() == 0
            assert x[1].max() == 0
            assert x[2].max() == 0
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test5(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = [
                factory.make_int_var(cp, -5, 0),
                factory.make_int_var(cp, -5, 0),
                factory.make_int_var(cp, -3, 0),
            ]
            cp.post(constraint.Sum(x, v=0))
            assert x[0].min() == 0
            assert x[1].min() == 0
            assert x[2].min() == 0
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test6(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = [
                factory.make_int_var(cp, -5, 0),
                factory.make_int_var(cp, -5, 0),
                factory.make_int_var(cp, -3, 3),
            ]
            cp.post(constraint.Sum(x, v=0))
            assert x[0].min() == -3
            assert x[1].min() == -3
            x[2].remove_above(0)
            cp.fix_point()
            assert x[0].min() == 0
            assert x[1].min() == 0
            assert x[2].min() == 0
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test7(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = [
                factory.make_int_var(cp, -5, 0),
                factory.make_int_var(cp, -5, 0),
                factory.make_int_var(cp, -3, 3),
            ]
            cp.post(constraint.Sum(x, v=0))
            assert x[0].min() == -3
            assert x[1].min() == -3
            x[2].remove(1)
            x[2].remove(2)
            x[2].remove(3)
            x[2].remove(4)
            x[2].remove(5)
            cp.fix_point()
            assert x[0].min() == 0
            assert x[1].min() == 0
            assert x[2].min() == 0
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test8(self, by_copy: "bool") -> "None":
        try:
            # {0,0,0},  1
            # {-2,1,1}  3
            # {2,-1,-1} 3
            # {-1,1,0}  6
            # {0,-3,3}  6
            # {2,-2,0}  6
            # {-1,1,0}  6
            # {1,2,-3}  6
            cp = factory.make_solver(by_copy)
            x = [
                factory.make_int_var(cp, -3, 3),
                factory.make_int_var(cp, -3, 3),
                factory.make_int_var(cp, -3, 3),
            ]
            cp.post(constraint.Sum(x, v=0))
            search = factory.make_dfs(cp, branching_scheme.first_fail(x))
            stats = search.solve()
            assert stats.number_of_solutions() == 37
        except exceptions.InconsistencyException:
            assert False  # Should not fail

    @pytest.mark.parametrize("by_copy", [False, True])
    def test9(self, by_copy: "bool") -> "None":
        cp = factory.make_solver(by_copy)
        x = [factory.make_int_var(cp, -9, -9)]
        try:
            cp.post(constraint.Sum(x, v=0))
            assert False  # should fail
        except exceptions.InconsistencyException:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test10(self, by_copy: "bool") -> "None":
        cp = factory.make_solver(by_copy)
        x = [factory.make_int_var(cp, -9, -4)]
        try:
            cp.post(constraint.Sum(x, v=0))
            assert False  # should fail
        except exceptions.InconsistencyException:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test11(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = self._make_i_var(cp, [-2147483645, -2147483639, -2147483637])
            y = self._make_i_var(cp, [-2147483645, -2147483638])
            cp.post(factory.Sum([x], y))
            assert False  # should fail
        except exceptions.InconsistencyException:
            pass
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test12(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x = self._make_i_var(cp, [-45, -39, -37])
            y = self._make_i_var(cp, [-45, -3])
            cp.post(factory.Sum([x], y))
        except exceptions.InconsistencyException:
            assert False  # Should not fail
        except NotImplementedError:
            pass

    @pytest.mark.parametrize("by_copy", [False, True])
    def test_over_flow_13(self, by_copy: "bool") -> "None":
        try:
            cp = factory.make_solver(by_copy)
            x0 = self._make_i_var(cp, [-463872433, -463872431, -463872430, -463872429])
            x1 = self._make_i_var(cp, [-463872438, -463872437, -463872430])
            x2 = self._make_i_var(cp, [-463872432, -463872429])
            x3 = self._make_i_var(
                cp,
                [
                    -463872435,
                    -463872434,
                    -463872432,
                    -463872431,
                    -463872430,
                    -463872429,
                ],
            )
            x4 = self._make_i_var(
                cp,
                [
                    -463872437,
                    -463872436,
                    -463872435,
                    -463872432,
                    -463872431,
                    -463872430,
                    -463872429,
                ],
            )
            cp.post(factory.less_or_equal(factory.sum_var([x0, x1, x2, x3, x4]), 0))
        except OverflowError:
            pass
        except NotImplementedError:
            pass

    def _make_i_var(self, cp: "solver.Solver", values: list[int]) -> "int_var.IntVar":
        return factory.make_int_var(cp, values=set(values))


class TestGraph:
    # TODO
    pass


class TestMaximumMatching:
    # TODO
    pass


class TestAllDifferentDC:
    # TODO
    pass


class TestAllDifferentFWC:
    # TODO
    pass


class TestCircuit:
    # TODO
    pass


class TestProfile:
    # TODO
    pass


class TestCumulative:
    # TODO
    pass


class TestCumulativeDecomposition:
    # TODO
    pass


class TestThetaTree:
    # TODO
    pass


class TestDisjunctive:
    # TODO
    pass


class TestDisjunctiveBinary:
    # TODO
    pass


class TestElement1DDomainConsistent:
    # TODO
    pass


class TestElement1DVar:
    # TODO
    pass


class TestIsLessOrEqualVar:
    # TODO
    pass


class TestIsOr:
    # TODO
    pass


class TestOr:
    # TODO
    pass


class TestTableCT:
    # TODO
    pass


class TestTableDecomp:
    # TODO
    pass
