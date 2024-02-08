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

from mini_cp.engine import state


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_bool(sm: "state.StateManager") -> "None":

    b1 = sm.make_state_ref(True)
    b2 = sm.make_state_ref(False)

    sm.save_state()
    b1.set_value(True)
    b1.set_value(False)
    b1.set_value(True)

    b2.set_value(False)
    b2.set_value(True)

    sm.restore_state()

    assert b1.value() is True
    assert b2.value() is False


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_bug_magic_on_restore(sm: "state.StateManager") -> "None":

    a = sm.make_state_ref(True)
    # level 0, a is true

    sm.save_state()  # level 1, a is true recorded
    sm.save_state()  # level 2, a is true recorded

    a.set_value(False)
    sm.restore_state()  # level 1, a is true

    a.set_value(False)  # level 1, a is false

    sm.save_state()  # level 2, a is false recorded

    sm.restore_state()  # level 1, a is false
    sm.restore_state()  # level 0, a is true

    assert a.value() is True


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_int1(sm: "state.StateManager") -> "None":
    # Two reversible ints inside the sm

    a = sm.make_state_int(5)
    b = sm.make_state_int(9)

    a.set_value(7)
    b.set_value(13)

    # Record current state a = 7, b = 1 and increase the
    # level to 0
    sm.save_state()
    assert sm.get_level() == 0

    a.set_value(10)
    b.set_value(13)
    a.set_value(11)

    # Record current state a = 11, b = 13 and increase
    # the level to 1
    sm.save_state()
    assert sm.get_level() == 1

    a.set_value(4)
    b.set_value(9)

    # Restore the state recorded at the top level 1: a=11, b=13
    # and remove the state of that level
    sm.restore_state()

    assert a.value() == 11
    assert b.value() == 13
    assert sm.get_level() == 0

    # Restore the state recorded at the top level 0: a=7, b=13
    # and remove the state of that level
    sm.restore_state()

    assert a.value() == 7
    assert b.value() == 13
    assert sm.get_level() == -1


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_int2(sm: "state.StateManager") -> "None":
    a = sm.make_state_int(5)
    b = sm.make_state_int(5)
    assert a.value() == 5
    a.set_value(7)
    b.set_value(13)
    assert a.value() == 7

    sm.save_state()

    a.set_value(10)
    assert a.value() == 10
    a.set_value(11)
    assert a.value() == 11
    b.set_value(16)
    b.set_value(15)

    sm.restore_state()
    assert a.value() == 7
    assert b.value() == 13


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_int_pop_until(sm: "state.StateManager") -> "None":
    a = sm.make_state_int(5)
    b = sm.make_state_int(5)

    a.set_value(7)
    b.set_value(13)
    a.set_value(13)
    sm.save_state()  # level 0

    a.set_value(5)
    b.set_value(10)
    c = sm.make_state_int(5)
    sm.save_state()  # level 1

    a.set_value(8)
    b.set_value(1)
    c.set_value(10)
    sm.save_state()  # level 2

    a.set_value(10)
    b.set_value(13)
    b.set_value(16)
    sm.save_state()  # level 3

    a.set_value(8)
    b.set_value(10)
    sm.restore_state_until(0)
    sm.save_state()  # level 1

    assert a.value() == 5
    assert b.value() == 10
    assert c.value() == 5

    a.set_value(8)
    b.set_value(10)
    b.set_value(8)
    b.set_value(10)
    sm.restore_state_until(0)

    assert a.value() == 5
    assert b.value() == 10
    assert c.value() == 5


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_int_pop_until_easy(sm: "state.StateManager") -> "None":
    a = sm.make_state_int(5)

    a.set_value(7)
    a.set_value(13)

    sm.save_state()  # level 0
    a.set_value(6)

    sm.save_state()  # level 1
    a.set_value(8)
    sm.save_state()  # level 2
    a.set_value(10)
    sm.save_state()  # level 3
    a.set_value(8)

    sm.restore_state_until(0)
    sm.save_state()  # level 1

    assert a.value() == 6
    a.set_value(8)

    sm.restore_state_until(0)
    assert a.value() == 6


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_sparse_set(sm: "state.StateManager") -> "None":

    sparse_set = state.StateSparseSet(sm, 9, 0)

    sm.save_state()
    sparse_set.remove(4)
    sparse_set.remove(6)
    assert sparse_set.contains(4) is False
    assert sparse_set.contains(6) is False

    sm.restore_state()
    assert sparse_set.contains(4) is True
    assert sparse_set.contains(6) is True


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_reversible_sparse_set(sm: "state.StateManager") -> "None":
    sparse_set = state.StateSparseSet(sm, 10, 0)

    assert set(sparse_set.to_array()) == {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
    sm.save_state()

    sparse_set.remove(1)
    sparse_set.remove(0)
    assert sparse_set.min() == 2

    sparse_set.remove(8)
    sparse_set.remove(9)

    assert set(sparse_set.to_array()) == {2, 3, 4, 5, 6, 7}
    assert sparse_set.max() == 7

    sm.restore_state()
    sm.save_state()

    assert sparse_set.size() == 10

    for i in range(10):
        assert sparse_set.contains(i) is True
    assert sparse_set.contains(10) is False

    assert sparse_set.min() == 0
    assert sparse_set.max() == 9

    sparse_set.remove_all_but(2)

    for i in range(10):
        if i != 2:
            assert sparse_set.contains(i) is False

    assert sparse_set.contains(2) is True
    assert set(sparse_set.to_array()) == {2}
    sm.restore_state()
    sm.save_state()

    assert sparse_set.size() == 10


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_sparse_set_range_constructor(sm: "state.StateManager") -> "None":
    sparse_set = state.StateSparseSet(sm, 10, 0)

    for i in range(10):
        assert sparse_set.contains(i) is True

    sm.save_state()
    sparse_set.remove(4)
    sparse_set.remove(5)
    sparse_set.remove(0)
    sparse_set.remove(1)

    assert sparse_set.min() == 2
    assert sparse_set.max() == 9
    sm.save_state()

    sparse_set.remove_all_but(7)
    assert sparse_set.min() == 7
    assert sparse_set.max() == 7
    sm.restore_state()
    sm.restore_state()

    for i in range(10):
        assert sparse_set.contains(i) is True


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_sparse_set_remove_below(sm: "state.StateManager") -> "None":
    sparse_set = state.StateSparseSet(sm, 10, 0)

    for i in range(10):
        assert sparse_set.contains(i) is True

    sm.save_state()
    sparse_set.remove_below(5)
    assert sparse_set.min() == 5
    assert sparse_set.max() == 9
    sm.save_state()
    sparse_set.remove(7)
    sparse_set.remove_below(7)
    assert sparse_set.min() == 8
    sm.restore_state()
    sm.restore_state()

    for i in range(10):
        assert sparse_set.contains(i) is True


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_sparse_set_remove_above(sm: "state.StateManager") -> "None":
    sparse_set = state.StateSparseSet(sm, 10, 0)

    for i in range(10):
        assert sparse_set.contains(i) is True

    sm.save_state()
    sparse_set.remove(1)
    sparse_set.remove(2)
    sparse_set.remove_above(7)

    assert sparse_set.min() == 0
    assert sparse_set.max() == 7
    sm.save_state()
    sparse_set.remove_above(2)

    assert sparse_set.max() == 0
    sm.restore_state()
    sm.restore_state()

    for i in range(10):
        assert sparse_set.contains(i) is True


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_sparse_bit_set_intersects(sm: "state.StateManager") -> "None":
    try:
        bit_set = state.StateSparseBitSet(sm, 256)

        b1 = state._SupportBitSet(bit_set)  # [0..59] U [130..255]
        b2 = state._SupportBitSet(bit_set)  # [60..129]
        b3 = state._SupportBitSet(bit_set)  # empty

        b1s = "[0..59] U [130..255]"
        b2s = "[60..129]"
        b3s = "empty bitset"

        for i in range(256):
            if i < 60 or i >= 130:
                b1.set(i)
            else:
                b2.set(i)

        bit_set.and_(b1)  # set is now [0..59] U [130..255]
        sets: "str" = b1s
        assert (
            bit_set.intersects(b1) is True
        ), f"You did not detect an intersection between {sets} and {b1s})"
        assert (
            bit_set.intersects(b2) is False
        ), f"You said that there is an intersection between {sets} and {b2s}"
        sm.save_state()
        bit_set.and_(b3)  # set is not empty

        sets = b3s
        assert (
            bit_set.intersects(b1) is False
        ), f"You said that there is an intersection between {sets} and {b1s}"
        assert (
            bit_set.intersects(b2) is False
        ), f"You said that there is an intersection between {sets} and {b2s}"
        assert (
            bit_set.intersects(b3) is False
        ), f"You said that there is an intersection between {sets} and {b3s}"

        sm.restore_state()
        sets = b1s
        assert (
            bit_set.intersects(b1) is True
        ), f"You did not detect an intersection between {sets} and {b1s})"
        assert (
            bit_set.intersects(b2) is False
        ), f"You said that there is an intersection between {sets} and {b2s}"
    except NotImplementedError:
        pass


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_empty_state_sparse_bit_set(sm: "state.StateManager") -> "None":
    try:
        bit_set = state.StateSparseBitSet(sm, 0)
        b1 = state._SupportBitSet(bit_set)
        assert bit_set.intersects(b1) is False
    except NotImplementedError:
        pass


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_sparse_bit_set_intersects_residue_only1(
    sm: "state.StateManager",
) -> "None":
    try:
        bit_set = state.StateSparseBitSet(sm, 256)
        b1 = state._SupportBitSet(bit_set)  # [128..255]
        b2 = state._SupportBitSet(bit_set)  # [0..255]
        b1s = "[128..255]"
        b2s = "[0..255]"
        between = f"between {b1s} and {b2s}"

        for i in range(256):
            b2.set(i)
            if i >= 128:
                b1.set(i)
        bit_set.and_(b2)  # set is now [0..255]

        # manually set the residue to 0: nothing is selected;
        b1._residue = 0
        assert (
            bit_set.intersects_residue_only(b1) is False
        ), f"There is no intersection {between} at word 0"
        # residue select the indices [64..127]
        b1._residue = 1
        assert (
            bit_set.intersects_residue_only(b1) is False
        ), f"There is no intersection {between} at word 1"
        # residue select the indices [128..191]
        b1._residue = 2
        assert (
            bit_set.intersects_residue_only(b1) is True
        ), f"There is no intersection {between} at word 2"
        # residue select the indices [192..255]
        b1._residue = 3
        assert (
            bit_set.intersects_residue_only(b1) is True
        ), f"There is no intersection {between} at word 3"
    except NotImplementedError:
        pass


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_sparse_bit_set_intersects_residue_only2(
    sm: "state.StateManager",
) -> "None":
    try:
        bit_set = state.StateSparseBitSet(sm, 256)
        b_set = state._SupportBitSet(bit_set)  # [123..194]
        b1 = state._SupportBitSet(bit_set)  # [110..180]
        b2 = state._SupportBitSet(bit_set)  # [181..200]
        bs = "[123..194]"
        b1s = "[128..255]"
        b2s = "[0..255]"
        between1 = f"between {bs} and {b1s}"
        between2 = f"between {bs} and {b2s}"

        for i in range(256):
            if i >= 123 and i <= 194:
                b_set.set(i)
            if i >= 110 and i <= 180:
                b1.set(i)
            if i >= 181 and i <= 200:
                b2.set(i)
        bit_set.and_(b_set)  # set is now [123..194]

        # manually set the residue to 0: nothing is selected;
        b1._residue = 0
        assert (
            bit_set.intersects_residue_only(b1) is False
        ), f"There is no intersection {between1} at word 0"
        b2._residue = 0
        assert (
            bit_set.intersects_residue_only(b2) is False
        ), f"There is no intersection {between2} at word 0"

        # residue select the indices [64..127]
        b1._residue = 1
        assert (
            bit_set.intersects_residue_only(b1) is False
        ), f"There is no intersection {between1} at word 1"
        b2._residue = 1
        assert (
            bit_set.intersects_residue_only(b2) is False
        ), f"There is no intersection {between2} at word 1"

        # residue select the indices [128..191]
        b1._residue = 2
        assert (
            bit_set.intersects_residue_only(b1) is True
        ), f"There is no intersection {between1} at word 2"
        b2._residue = 2
        assert (
            bit_set.intersects_residue_only(b2) is True
        ), f"There is no intersection {between2} at word 2"

        # residue select the indices [192..255]
        b1._residue = 3
        assert (
            bit_set.intersects_residue_only(b1) is True
        ), f"There is no intersection {between1} at word 3"
        b2._residue = 3
        assert (
            bit_set.intersects_residue_only(b2) is True
        ), f"There is no intersection {between2} at word 3"

    except NotImplementedError:
        pass


@pytest.mark.parametrize("sm", [state.Copier(), state.Trailer()])
def test_state_sparse_bit_set_residue(sm: "state.StateManager") -> "None":
    try:
        bit_set = state.StateSparseBitSet(sm, 256)
        b1 = state._SupportBitSet(bit_set)  # [64..255]

        for i in range(256):
            if i >= 64:
                b1.set(i)

        bit_set.and_(b1)  # set is now [0..59] U [130..255]
        # residue has by default value (i.e. 0)
        assert (
            b1._residue == 0
        ), "You shouldn't be modifying the initial value of the residue"

        sm.save_state()
        bit_set.intersects(b1)

        r = b1._residue
        # word 0 is empty, new residue should have been found
        assert b1._residue != 0, "You are not updating the value of the residue"
        sm.restore_state()  # set is now [0..59] U [130..255]
        bit_set.intersects(b1)  # residue still leading to an intersection

        # no change should have been done to the residue
        assert b1._residue == r, "The value of the residue should not be restored"

    except NotImplementedError:
        pass
