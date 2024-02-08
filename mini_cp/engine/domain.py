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

from mini_cp.engine import state


class DomainListener(abc.ABC):
    """Domain listeners are passed as argument
    to the IntDomain modifier methods."""

    @abc.abstractmethod
    def empty(self) -> "None":
        """Called whenever the domain becomes empty."""

    @abc.abstractmethod
    def fix(self) -> "None":
        """Called whenever the domain becomes a single value."""

    @abc.abstractmethod
    def change(self) -> "None":
        """Called whenever the domain loses a value."""

    @abc.abstractmethod
    def change_min(self) -> "None":
        """Called whenever the minimum value of the domain is lost."""

    @abc.abstractmethod
    def change_max(self) -> "None":
        """Called whenever the maximum value of the domain is lost."""


class IntDomain(abc.ABC):
    """Interface for integer domain implementation.
    A domain is encapsulated in an IntVar implementation.
    A domain is like a set of integers.
    """

    @abc.abstractmethod
    def min(self) -> "int":
        """Returns the minimum value of the domain."""

    @abc.abstractmethod
    def max(self) -> "int":
        """Returns the maximum value of the domain."""

    @abc.abstractmethod
    def size(self) -> "int":
        """Returns the cardinality of the domain."""

    @abc.abstractmethod
    def contains(self, v: "int") -> "bool":
        """Checks if the specified value belongs to the domain.
        'v': the value to be tested
        Returns true if v belongs to the domain, false otherwise.
        """

    @abc.abstractmethod
    def is_singleton(self) -> "bool":
        """Checks if the domain contains a single element.
        Returns true if the domain contains a single element,
        false otherwise.
        """

    @abc.abstractmethod
    def remove(self, v: "int", l: "DomainListener") -> "None":
        """Removes a value from the domain and notifies appropriately the
        listener.
        'v': the value to be removed
        'l': the methods of the listener are notified as follows:
              DomainListener change() is called if v belongs to the domain
              DomainListener change_max() is called if v is equal to the maximum
              value
              DomainListener change_min() is called if v is equal to the minimum
              value
              DomainListener fix() is called if v belongs to the domain and after
              its removal the domain has a single value
              DomainListener empty() is called if v is the last value in the
              domain i.e., the domain is empty after this operation
        """

    @abc.abstractmethod
    def remove_all_but(self, v: "int", l: "DomainListener") -> "None":
        """Removes every value from the domain except the specified one.
        'v': the value to be kept
        'l': the methods of the listener are notified as follows:
              DomainListener change() is called if some value is removed during
              the operation
              DomainListener change_max() is called if v is not equal to the
              maximum value
              DomainListener change_min() is called if v is not equal to the
              minimum value
              DomainListener fix() is called if v belongs to the domain and
              after its removal the domain has a single value
              DomainListener empty() is called if v is not in the domain i.e.
              the domain is empty after this operation
        """

    @abc.abstractmethod
    def remove_below(self, v: "int", l: "DomainListener") -> "None":
        """Removes every value less than the specified value from the domain.
        'v': the value such that all the values less than v are removed
        'l': the methods of the listener are notified as follows:
              DomainListener change() is called if some value is removed during
              the operation
              DomainListener change_max() is called if v is larger than the
              minimum value
              DomainListener fix() is called if v is equal to the
              maximum value
              DomainListener empty() is called if v is larger than the
              maximum value i.e. the domain is empty after this operation
        """

    @abc.abstractmethod
    def remove_above(self, v: "int", l: "DomainListener") -> "None":
        """Removes every value larger than the specified value from the domain.
        'v': the value such that all the values larger than v are removed
        'l': the methods of the listener are notified as follows:
              DomainListener change() is called if some value is removed during
              the operation
              DomainListener change_max() is called if v is less than the
              maximum value
              DomainListener fix() is called if v is equal to the minimum value
              DomainListener empty() is called if v is less than the minimum
              value i.e. the domain is empty after this operation
        """

    @abc.abstractmethod
    def fill_array(self, dest: "list[int]") -> "int":
        """Copies the values of the domain into an array.
        'dest': an array large enough {len(dest) >= size()}
        Returns the size of the domain and dest[0,...,size-1] contains the
        values in the domain in an arbitrary order.
        """

    @abc.abstractmethod
    def __str__(self) -> "str":
        pass


class SparseSetDomain(IntDomain):
    """Implementation of a domain with a sparse-set."""

    def __init__(self, sm: "state.StateManager", min: "int", max: "int"):
        self._domain: "state.StateSparseSet" = state.StateSparseSet(
            sm, max - min + 1, min
        )

    def fill_array(self, dest: "list[int]") -> "int":
        return self._domain.fill_array(dest)

    def min(self) -> "int":
        return self._domain.min()

    def max(self) -> "int":
        return self._domain.max()

    def size(self) -> "int":
        return self._domain.size()

    def contains(self, v: "int") -> "bool":
        return self._domain.contains(v)

    def is_singleton(self) -> "bool":
        return self._domain.size() == 1

    def remove(self, v: "int", l: "DomainListener") -> "None":
        if self._domain.contains(v):
            max_changed = self.max() == v
            min_changed = self.min() == v
            self._domain.remove(v)
            if self._domain.size() == 0:
                l.empty()
            l.change()
            if max_changed:
                l.change_max()
            if min_changed:
                l.change_min()
            if self._domain.size() == 1:
                l.fix()

    def remove_all_but(self, v: "int", l: "DomainListener") -> "None":
        if self._domain.contains(v):
            if self._domain.size() != 1:
                max_changed = self.max() != v
                min_changed = self.min() != v
                self._domain.remove_all_but(v)
                if self._domain.size() == 0:
                    l.empty()
                l.fix()
                l.change()
                if max_changed:
                    l.change_max()
                if min_changed:
                    l.change_min()
        else:
            self._domain.remove_all()
            l.empty()

    def remove_below(self, value: "int", l: "DomainListener") -> "None":
        if self._domain.min() < value:
            self._domain.remove_below(value)
            if self._domain.size() == 0:
                l.empty()
            elif self._domain.size() == 1:
                l.fix()
                l.change_min()
                l.change()
            else:
                l.change_min()
                l.change()

    def remove_above(self, value: "int", l: "DomainListener") -> "None":
        if self._domain.max() > value:
            self._domain.remove_above(value)
            if self._domain.size() == 0:
                l.empty()
            elif self._domain.size() == 1:
                l.fix()
                l.change_max()
                l.change()
            else:
                l.change_max()
                l.change()

    def __str__(self) -> "str":
        if self.size() == 0:
            return "{}"
        b = ["{"]
        for i in range(self.min(), self.max()):
            if self.contains(i):
                b.append(f"{i},")
        b.append(f"{self.max()}")
        b.append("}")
        return "".join(b)
