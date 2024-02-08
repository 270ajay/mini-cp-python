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

import abc
import collections
from typing import Callable, TypeVar

_T = TypeVar("_T")
_K = TypeVar("_K")
_V = TypeVar("_V")


class State(abc.ABC):
    """Object that wraps a reference and
    can be saved and restored through the
    StateManager save_state() / StateManager restore_state()
    methods.
    See StateManager make_state_ref(object) for the creation.
    """

    @abc.abstractmethod
    def set_value(self, value: "_T") -> "_T":
        """Sets the value."""

    @abc.abstractmethod
    def value(self) -> "_T":
        """Retrieves the value."""

    @abc.abstractmethod
    def __str__(self) -> "str":
        pass


class StateManager(abc.ABC):
    """The StateManager interface exposes all the mechanisms and
    data structures needed to implement a depth-first-search with
    reversible states."""

    @abc.abstractmethod
    def save_state(self) -> "None":
        """Stores the current state such that it
        can be recovered by using restore_state().
        Increase the level by 1."""

    @abc.abstractmethod
    def restore_state(self) -> "None":
        """Restores state as it was at get_level() - 1.
        Decrease the level by 1."""

    @abc.abstractmethod
    def restore_state_until(self, level: "int") -> "None":
        """Restores the state up the given level.
        The level, a non-negative number between 0 and get_level().
        """

    @abc.abstractmethod
    def on_restore(self, listener_closure: "Callable[[], None]") -> "None":
        """Add a listener that is notified each time that restore_state()
        is called.
        listener_closure: the listener to be notified."""

    @abc.abstractmethod
    def get_level(self) -> "int":
        pass

    @abc.abstractmethod
    def make_state_ref(self, init_value: "_T") -> "State":
        """Creates a stateful reference (restorable)."""

    @abc.abstractmethod
    def make_state_int(self, init_value: "int") -> "StateInt":
        """Creates a stateful integer (restorable)"""

    @abc.abstractmethod
    def make_state_map(self) -> "StateMap":
        """Creates a stateful map (restorable)"""

    @abc.abstractmethod
    def with_new_state(self, body: "Callable[[], None]") -> "None":
        """Higher-order function that preserves the state prior to
        calling 'body' and restores it after.
        'body': the first-order function to execute.
        """


class StateInt(State, abc.ABC):
    """Object that wraps an integer value
    that can be saved and restored through the
    StateManager save_state() / StateManager restore_state()
    methods.
    See StateManager make_state_int(int) for the creation.
    """

    def increment(self) -> "int":
        """Increments the value.
        Returns the new value.
        """
        return self.set_value(self.value() + 1)

    def decrement(self) -> "int":
        """Decrements the value.
        Returns the new value.
        """
        return self.set_value(self.value() - 1)


class StateMap(abc.ABC):
    """A generic map that can revert its state with
    StateManager save_state() / StateManager restore_state()
    methods."""

    @abc.abstractmethod
    def put(self, k: "_K", v: "_V") -> "None":
        """Inserts the key-value pair.
        It erases the existing ones if the
        map already contains an entry with
        the given key.
        k: the key
        v: the value
        """

    @abc.abstractmethod
    def get(self, k: "_K") -> "_V":
        """Retrieves the value for a given key.
        k: the key
        v: the value if the entry (k,v) was previously put,
        None otherwise
        """


class StateSparseSet:
    """Set implemented using a sparse-set data structure
    that can be saved and restored through the
    StateManager save_state() / StateManager restore_state()
    methods.
    """

    def __init__(self, sm: "StateManager", n: "int", ofs: "int"):
        """Creates a set containing the elements {ofs,ofs+1,...,ofs+n-1}
        'sm': the state manager that will save and restore the set when
        StateManager save_state() / StateManager restore_state() methods
        are called
        'n': the number of elements in the set
        'ofs': the minimum value in the set containing {ofs,ofs+1,...,ofs+n-1}
        """
        self._n: "int" = n
        self._ofs: "int" = ofs
        self._size: "StateInt" = sm.make_state_int(n)
        self._min: "StateInt" = sm.make_state_int(0)
        self._max: "StateInt" = sm.make_state_int(n - 1)
        self._values: "list[int]" = [i for i in range(n)]
        self._indices: "list[int]" = [i for i in range(n)]

    def _exchange_positions(self, val1: "int", val2: "int") -> "None":
        assert self._check_val(val1)
        assert self._check_val(val2)
        v1 = val1
        v2 = val2
        i1 = self._indices[v1]
        i2 = self._indices[v2]
        self._values[i1] = v2
        self._values[i2] = v1
        self._indices[v1] = i2
        self._indices[v2] = i1

    def _check_val(self, val: "int") -> "bool":
        assert val <= len(self._values) - 1
        return True

    def to_array(self) -> "list[int]":
        """Returns an array with the values present in the set."""
        res = [0] * self.size()
        self.fill_array(res)
        return res

    def fill_array(self, dest: "list[int]") -> "int":
        """Sets the first values of 'dest' to the ones
        present in the set.
        'dest': an array large enough {len(dest) >= self.size()}
        Returns the size of the set.
        """
        s = self._size.value()
        for i in range(s):
            dest[i] = self._values[i] + self._ofs
        return s

    def is_empty(self) -> "bool":
        """Checks if the set is empty.
        Returns true if the set is empty.
        """
        return self._size.value() == 0

    def size(self) -> "int":
        """Returns the size of the set."""
        return self._size.value()

    def min(self) -> "int":
        """Returns the minimum value in the set."""
        if self.is_empty():
            raise ValueError()
        return self._min.value() + self._ofs

    def max(self) -> "int":
        """Returns the maximum value in the set."""
        if self.is_empty():
            raise ValueError()
        return self._max.value() + self._ofs

    def _update_bounds_val_removed(self, val: "int") -> "None":
        self._update_max_val_removed(val)
        self._update_min_val_removed(val)

    def _update_max_val_removed(self, val: "int") -> "None":
        if not self.is_empty() and self._max.value() == val:
            assert not self._internal_contains(val)
            # the maximum was removed, search the new one
            for v in range(val - 1, self._min.value() - 1, -1):
                if self._internal_contains(v):
                    self._max.set_value(v)
                    return

    def _update_min_val_removed(self, val: "int") -> "None":
        if not self.is_empty() and self._min.value() == val:
            assert not self._internal_contains(val)
            # the minimum was removed, search the new one
            for v in range(val + 1, self._max.value() + 1):
                if self._internal_contains(v):
                    self._min.set_value(v)
                    return

    def _internal_contains(self, val: "int") -> "bool":
        """This method operates on the shifted value (one cannot shift now)
        'val': the set_value to lookup for membership
        Returns true if val is in the set, false otherwise.
        """
        if val < 0 or val >= self._n:
            return False
        else:
            return self._indices[val] < self.size()

    def remove(self, val: "int") -> "bool":
        """Removes the given value from the set.
        'val': the value to remove.
        Returns True if val was in the set, false otherwise.
        """
        if not self.contains(val):
            return False  # the set_value has already been removed
        val -= self._ofs
        assert self._check_val(val)
        s = self.size()
        self._exchange_positions(val, self._values[s - 1])
        self._size.decrement()
        self._update_bounds_val_removed(val)
        return True

    def contains(self, val: "int") -> "bool":
        """Checks if a value is in the set.
        Returns true if val is in the set.
        """
        val -= self._ofs
        if val < 0 or val >= self._n:
            return False
        else:
            return self._indices[val] < self.size()

    def remove_all_but(self, v: "int") -> "None":
        """Removes all the elements from the set except the given value.
        'v': an element in the set
        """
        # we only have to put this set_value in the first position and
        # set the size to 1
        assert self.contains(v)
        v -= self._ofs
        assert self._check_val(v)
        val = self._values[0]
        index = self._indices[v]
        self._indices[v] = 0
        self._values[0] = v
        self._indices[val] = index
        self._values[index] = val
        self._min.set_value(v)
        self._max.set_value(v)
        self._size.set_value(1)

    def remove_all(self) -> "None":
        """Removes all the values in the set."""
        self._size.set_value(0)

    def remove_below(self, value: "int") -> "None":
        """Remove all the values less than the given value from the set.
        'value': a value such that all the ones smaller are removed.
        """
        if self.max() < value:
            self.remove_all()
        else:
            for v in range(self.min(), value):
                self.remove(v)

    def remove_above(self, value: "int") -> "None":
        """Remove all the values larger than the given value from the set.
        'value': a value such that all the ones greater are removed.
        """
        if self.min() > value:
            self.remove_all()
        else:
            for v in range(self.max(), value, -1):
                self.remove(v)

    def __str__(self) -> "str":
        b = ["{"]
        for i in range(0, self.size() - 1):
            b.append(f"{self._values[i] + self._ofs}")
            b.append(",")
        if self.size() > 0:
            b.append(f"{self._values[self.size() - 1] + self._ofs}")
        b.append("}")
        return "".join(b)


class StateStack:
    """Generic Stack that can be saved and restored through
    the StateManager save_state() / StateManager restore_state()
    methods.
    """

    def __init__(self, sm: "StateManager"):
        """Creates a restorable stack.
        'sm' the state manager that saves/restores the stack
        when StateManager save_state() / StateManager restore_state()
        methods are called.
        """
        self._size: "StateInt" = sm.make_state_int(0)
        self._stack: "list[_T]" = []

    def push(self, elem: "_T") -> "None":
        s = self._size.value()
        if len(self._stack) > s:
            self._stack[s] = elem
        else:
            self._stack.append(elem)
        self._size.increment()

    def size(self) -> "int":
        return self._size.value()

    def get(self, index: "int") -> "_T":
        return self._stack[index]


class StateEntry(abc.ABC):
    """A StateEntry is aimed to be stored
    by a StateManager to revert some state"""

    @abc.abstractmethod
    def restore(self) -> "None":
        pass


class Storage(abc.ABC):
    """Object that can be saved by the Copier."""

    @abc.abstractmethod
    def save(self) -> "StateEntry":
        pass


class _CopyStateEntry(StateEntry):

    def __init__(self, v: "_T", copy: "Copy"):
        self._v: "_T" = v
        self._copy: "Copy" = copy

    def restore(self) -> "None":
        self._copy._v = self._v


class Copy(Storage, State):
    """Implementation of State with copy strategy
    See Copier
    See StateManager make_state_ref(Object)
    """

    def __init__(self, initial: "_T"):
        self._v: "_T" = initial

    def set_value(self, v: "_T"):
        self._v = v
        return v

    def value(self) -> "_T":
        return self._v

    def __str__(self) -> "str":
        return str(self._v)

    def save(self) -> "StateEntry":
        return _CopyStateEntry(self._v, self)


class CopyInt(Copy, StateInt):
    """Implementation of StateInt with copy strategy
    See Copier
    See StateManager make_state_int(int)
    """

    def __init__(self, initial: "int"):
        super().__init__(initial)


class CopyMap(StateMap, Storage):
    """Implementation of StateMap with copy strategy
    See Copier
    See StateManager make_state_map()
    """

    def __init__(self, m: "dict[_K, _V]" = None):
        raise NotImplementedError

    def put(self, k: "_K", v: "_V") -> "None":
        raise NotImplementedError

    def get(self, k: "_K") -> "_V":
        raise NotImplementedError

    def save(self) -> "StateEntry":
        raise NotImplementedError


class _Backup(collections.deque[StateEntry]):

    def __init__(self, copier: "Copier"):
        super().__init__()
        for storage in copier._store:
            self.append(storage.save())

    def restore(self) -> "None":
        for state_entry in self:
            state_entry.restore()


class Copier(StateManager):
    """StateManager that will store the state
    of every created elements at each
    save_state() call.
    """

    def __init__(self):
        self._store: "collections.deque[Storage]" = collections.deque()
        self._prior: "collections.deque[_Backup]" = collections.deque()
        self._on_restore_listeners: "list[Callable[[], None]]" = []

    def _notify_restore(self) -> "None":
        for procedure in self._on_restore_listeners:
            procedure()

    def on_restore(self, listener: "Callable[[], None]") -> "None":
        self._on_restore_listeners.append(listener)

    def get_level(self) -> "int":
        return len(self._prior) - 1

    def store_size(self) -> "int":
        return len(self._store)

    def save_state(self) -> "None":
        self._prior.append(_Backup(self))

    def restore_state(self) -> "None":
        self._prior.pop().restore()
        self._notify_restore()

    def with_new_state(self, body: "Callable[[], None]") -> "None":
        level = self.get_level()
        self.save_state()
        body()
        self.restore_state_until(level)

    def restore_state_until(self, level: "int") -> "None":
        while self.get_level() > level:
            self.restore_state()

    def make_state_ref(self, init_value: "_T") -> "State":
        r = Copy(init_value)
        self._store.append(r)
        return r

    def make_state_int(self, init_value: "int") -> "StateInt":
        s = CopyInt(init_value)
        self._store.append(s)
        return s

    def make_state_map(self) -> "StateMap":
        s = CopyMap()
        self._store.append(s)
        return s

    def __str__(self) -> "str":
        return "Copier"


class _TrailStateEntry(StateEntry):

    def __init__(self, v: "_T", trail: "Trail"):
        self._v: "_T" = v
        self._trail: "Trail" = trail

    def restore(self) -> "None":
        self._trail._v = self._v


class Trail(State):
    """Implementation of State with trail strategy
    See Trailer
    See StateManager make_state_ref(Object)
    """

    def __init__(self, trail: "Trailer", initial: "_T"):
        self._trail: "Trailer" = trail
        self._v: "_T" = initial
        self._last_magic: "int" = trail.get_magic() - 1

    def trail(self) -> "None":
        trail_magic = self._trail.get_magic()
        if self._last_magic != trail_magic:
            self._last_magic = trail_magic
            self._trail.push_state(_TrailStateEntry(self._v, self))

    def set_value(self, v: "_T") -> "_T":
        if v != self._v:
            self.trail()
            self._v = v
        return self._v

    def value(self) -> "_T":
        return self._v

    def __str__(self) -> "str":
        return str(self._v)


class TrailInt(Trail, StateInt):
    """Implementation of StateInt with trail strategy
    See Trailer
    See StateManager make_state_int(int)
    """

    def __init__(self, trail: "Trailer", initial: "int"):
        super().__init__(trail, initial)


class TrailMap(StateMap):
    """Implementation of StateMap with trail strategy
    See Trailer
    See StateManager make_state_map()
    """

    def __init__(self, trail: "Trailer"):
        raise NotImplementedError("TrailMap")

    def put(self, k: "_K", v: "_V") -> "None":
        raise NotImplementedError("TrailMap")

    def get(self, k: "_K") -> "_V":
        raise NotImplementedError("TrailMap")


class _BackupTrail(collections.deque[StateEntry]):
    def __init__(self):
        super().__init__()

    def restore(self) -> "None":
        # Using for-loop on a stack gives the wrong order
        while self:
            self.pop().restore()


class Trailer(StateManager):
    """StateManager that will lazily store the
    state of state object at each save_state()
    call. Only the one that effectively change
    are stored and at most once between any
    call to save_state(). This can be seen as an
    optimized version of Copier.
    """

    def __init__(self):
        self._prior: "collections.deque[_BackupTrail]" = collections.deque()
        self._current: "_BackupTrail" = _BackupTrail()
        self._magic: "int" = 0
        self._on_restore_listeners: "list[Callable[[], None]]" = []

    def _notify_restore(self) -> "None":
        for procedure in self._on_restore_listeners:
            procedure()

    def on_restore(self, listener: "Callable[[], None]") -> "None":
        self._on_restore_listeners.append(listener)

    def get_magic(self) -> "int":
        return self._magic

    def push_state(self, entry: "StateEntry") -> "None":
        self._current.append(entry)

    def get_level(self) -> "int":
        return len(self._prior) - 1

    def save_state(self) -> "None":
        self._prior.append(self._current)
        self._current = _BackupTrail()
        self._magic += 1

    def restore_state(self) -> "None":
        self._current.restore()
        self._current = self._prior.pop()
        self._magic += 1
        self._notify_restore()

    def with_new_state(self, body: "Callable[[], None]") -> "None":
        level = self.get_level()
        self.save_state()
        body()
        self.restore_state_until(level)

    def restore_state_until(self, level: "int") -> "None":
        while self.get_level() > level:
            self.restore_state()

    def make_state_ref(self, init_value: "_T") -> "State":
        return Trail(self, init_value)

    def make_state_int(self, init_value: "int") -> "StateInt":
        return TrailInt(self, init_value)

    def make_state_map(self) -> "StateMap":
        return TrailMap(self)

    def __str__(self) -> "str":
        return "Trailer"


class StateInterval:
    """Implementation of an interval that can be saved
    and restored through the StateManager save_state() /
    StateManager restore_state() methods.
    """

    def __init__(self, sm: "StateManager", min: "int", max: "int"):
        """Creates an interval that can be saved and restored
        with the StateManager save_state / StateManager restore_state
        methods.
        'sm': The state-manager that save and restore the state of this interval
        'min': the minimum value of the interval
        'max': the maximum value of the interval {max >= min}
        """
        self._sm: "StateManager" = sm
        self._min: "StateInt" = sm.make_state_int(min)
        self._max: "StateInt" = sm.make_state_int(max)

    def is_empty(self) -> "bool":
        """Checks if the interval is empty.
        Returns true if the set is empty.
        """
        return self._min.value() > self._max.value()

    def size(self) -> "int":
        """Returns the number of integer values in the interval."""
        return max(self._max.value() - self._min.value() + 1, 0)

    def min(self) -> "int":
        """Returns the minimum value in the interval."""
        return self._min.value()

    def max(self) -> "int":
        """Returns the maximum value in the interval."""
        return self._max.value()

    def contains(self, val: "int") -> "bool":
        """Checks if a given value is in the interval.
        'val' the value to check
        Returns true if the value is in the interval
        """
        return self._min.value() <= val <= self._max.value()

    def fill_array(self, dest: "list[int]") -> "int":
        """Sets the first values of 'dest' to the ones
        present in the interval.
        'dest': an array large enough {len(dest) >= self.size()}
        Returns the size of the set
        """
        s = self.size()
        from_val = self.min()
        for i in range(s):
            dest[i] = from_val + i
        return s

    def remove_all_but(self, v: "int") -> "None":
        """Reduces the interval to a single value.
        'v' is an element in the set.
        """
        assert self.contains(v)
        self._min.set_value(v)
        self._max.set_value(v)

    def remove_all(self) -> "None":
        """Empties the interval."""
        self._min.set_value(self._max.value() + 1)

    def remove_below(self, value: "int") -> "None":
        """Updates the minimum value of the interval to
        the given one if it is larger than the current
        self.min().
        'value' the minimum to set
        """
        self._min.set_value(value)

    def remove_above(self, value: "int") -> "None":
        """Updates the maximum value of the interval to
        the given one if it is less than the current
        self.max().
        'value' the maximum to set
        """
        self._max.set_value(value)

    def __str__(self) -> "str":
        b = ["{", f"{self._min}...{self._max}", "}"]
        return "".join(b)


class StateLazySparseSet:
    """A sparse-set that lazily switch from a
    dense interval representation to a sparse-set
    representation when a hole is created in the interval.
    """


def _unsigned_right_bit_shift(val: "int", n: "int") -> "int":
    """https://stackoverflow.com/a/5833119"""
    return (val % 0x100000000) >> n


class _BitSet:
    """Bitset of the same capacity as the StateSparseBitSet
    It is not synchronized with StateManager
    It is rather intended to be used as parameter to the
    {and(BitSet)} method to modify the StateSparseBitSet
    """

    def __init__(self, state_sparse_bit_set: "StateSparseBitSet"):
        """Initializes a bit-set with the same capacity as the
        StateSparseBitSet. All the bits are initially unset. The set it
        represents is thus empty.
        """
        self._words: "list[int]" = [0] * state_sparse_bit_set._n_words
        self._state_sparse_bit_set: "StateSparseBitSet" = state_sparse_bit_set

    def set(self, i: "int") -> "None":
        """Sets the bit at the specified index to true."""
        v = 1 << i
        #  << is a cyclic shift, (1 << 64) == 1
        self._words[_unsigned_right_bit_shift(i, 6)] |= v

    def get(self, i: "int") -> "bool":
        """Gives the bit at the specified index."""
        word_index = _unsigned_right_bit_shift(i, 6)
        return (word_index < self._state_sparse_bit_set._n_words) and (
            (self._words[word_index] & 1 << i) != 0
        )

    def __str__(self) -> "str":
        res = [
            f" w{i}={str(self._words[i])}"
            for i in range(self._state_sparse_bit_set._n_words)
        ]
        return "".join(res)


class _SupportBitSet(_BitSet):
    def __init__(self, state_sparse_bit_set: "StateSparseBitSet"):
        super().__init__(state_sparse_bit_set)
        self._residue: "int" = 0


class _MaskBitSet(_BitSet):

    def __init__(self, state_sparse_bit_set: "StateSparseBitSet"):
        """Initializes a bit-set with the same capacity as the StateSparseBitSet.
        All the bits are initially unset. The set it represents is thus empty.
        """
        super().__init__(state_sparse_bit_set)

    def clear(self) -> "None":
        """Sets all the bits in this BitSet to false
        The clear is optimized to ignore the empty words in the
        associated Reversible Sparse Bit Set.
        """
        non_zero_idx = self._state_sparse_bit_set._non_zero_idx
        for i in range(self._state_sparse_bit_set._non_zero_size.value()):
            self._words[non_zero_idx[i]] = 0

    def or_(self, other: "_BitSet") -> "None":
        """Performs a logical OR of this bit set with the bit set argument. This
        bit set is modified so that a bit in it has the value true if and only if it
        either already had the value true or the corresponding bit in the bit set
        argument has the value true.
        The logical OR is optimized to ignore the empty words in the associated
        Reversible Sparse Bit Set.
        'other': the other bit-set to make the union with
        """
        non_zero_idx = self._state_sparse_bit_set._non_zero_idx
        for i in range(self._state_sparse_bit_set._non_zero_size.value()):
            self._words[non_zero_idx[i]] |= other._words[non_zero_idx[i]]

    def and_(self, other: "_BitSet") -> "None":
        """Performs a logical AND of this target bit set with the argument bit set. This
        bit set is modified so that each bit in it has the value true if and only if it
        both initially had the value true and the corresponding bit in the bit set
        argument also had the value true.
        The logical AND is optimized to ignore the empty words in the associated
        Reversible Sparse Bit Set.
        'other': the other bit-set to make the intersection with
        """
        non_zero_idx = self._state_sparse_bit_set._non_zero_idx
        for i in range(self._state_sparse_bit_set._non_zero_size.value()):
            self._words[non_zero_idx[i]] &= other._words[non_zero_idx[i]]


class StateSparseBitSet:
    """Class to represent a bit-set that can be saved and restored
    through the StateManager save_state() / StateManager restore_state()
    methods.
    """

    def __init__(self, sm: "StateManager", n: "int"):
        """Creates a StateSparseSEt with n bits, initially all set.
        'sm': the state manager
        'n': the number of bits
        """
        # Variables used to store value of the bitset
        self._n_words: int = _unsigned_right_bit_shift(n + 63, 6)  # Divided by 64
        self._words: list[State] = [
            sm.make_state_ref(0xFFFFFFFFFFFFFFFF) for _ in range(self._n_words)
        ]

        # Variables used to make set sparse
        self._non_zero_idx: list[int] = [i for i in range(self._n_words)]
        self._non_zero_size: StateInt = sm.make_state_int(self._n_words)

    def and_(self, bs: "_BitSet") -> "None":
        """Performs a logical AND of this target bit set with the argument
        bit set. This bit set is modified so that each bit in it has the value
        true if and only if it both initially had the value true and the
        corresponding bit in the bit set argument also had the value true.
        The Logical AND is optimized to ignore the empty words in the
        associated Reversible Sparse Bit Set
        'bs': the sparse-set to intersect with
        """
        for i in range(self._non_zero_size.value() - 1, -1, -1):
            w = self._words[self._non_zero_idx[i]]
            wn = w.value() & bs._words[self._non_zero_idx[i]]
            w.set_value(wn)
            if wn == 0:  # Swap with last non-zero word
                self._non_zero_size.decrement()
                tmp = self._non_zero_idx[i]
                self._non_zero_idx[i] = self._non_zero_idx[self._non_zero_size.value()]
                self._non_zero_idx[self._non_zero_size.value()] = tmp

    def is_empty(self) -> "bool":
        """Returns true if this BitSet contains no bits that are set to true."""
        return self._non_zero_size.value() == 0

    def intersects_residue_only(self, bs: "_SupportBitSet") -> "bool":
        """Returns true if, for the given {SupportBitSet words} id stored in by
        the {SupportBitSet residue} of the specified {SupportBitSet} bs, bs has any
        bits set to true that are also set to true in the corresponding
        {StateSparseBitSet words} of this BitSet.
        'bs': the bitset to test the intersection with
        Returns true if the intersection is non-empty
        """
        # TODO: Use the residue to test if the non-empty intersection stored
        #  is still non-empty
        raise NotImplementedError("StateSparseBitSet")

    def intersects(self, bs: "_SupportBitSet") -> "bool":
        """Returns true if the specified {SupportBitSet} has any bits set to true
        that are also set to true in this {StateSparseBitSet}.
        The intersection test is optimized to ignore the empty words in the
        associated Reversible Sparse Bit Set.
        'bs': the bitset to test the intersection with
        Returns True if the intersection is non-empty
        """
        if self.intersects_residue_only(bs):
            return True
        for i in range(self._non_zero_size.value() - 1, -1, -1):
            idx = self._non_zero_idx[i]
            w = self._words[idx]
            if (w.value() & bs._words[idx]) != 0:
                # TODO: Store the new non-empty intersection using
                #  residue of bs
                return True
        return False

    def get(self, i: "int") -> "bool":
        """Gives the bit at the specified index
        'i'" the bit to return
        Returns true if the bit at index i is set
        """
        word_index = _unsigned_right_bit_shift(i, 6)
        return (word_index < self._non_zero_size.value()) and (
            (self._words[word_index].value() & 1 << i) != 0
        )

    def __str__(self) -> "str":
        res = [
            f" w{self._non_zero_idx[i]}={str(self._words[self._non_zero_idx[i]].value())}"
            for i in range(self._non_zero_size.value())
        ]
        return "".join(res)
