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
from typing import Callable

from mini_cp.engine import constraint, domain, exceptions, solver, state

_MAX_VALUE = 2147483647
_MIN_VALUE = -2147483648


class IntVar(abc.ABC):
    """Integer variable interface."""

    @abc.abstractmethod
    def get_solver(self) -> "solver.Solver":
        """Returns the solver in which this variable was created."""

    @abc.abstractmethod
    def when_fixed(self, f: "Callable[[], None]") -> "None":
        """Asks that the closure is called whenever the domain
        of this variable is reduced to a single set_value.
        """

    @abc.abstractmethod
    def when_bound_change(self, f: "Callable[[], None]") -> "None":
        """Asks that the closure is called whenever
        the max or min set_value of the domain of this variable
        changes.
        """

    @abc.abstractmethod
    def when_domain_change(self, f: "Callable[[], None]") -> "None":
        """Asks that the closure is called whenever the domain
        of this variable changes.
        """

    @abc.abstractmethod
    def propagate_on_domain_change(self, c: "constraint.Constraint") -> "None":
        """Asks that Constraint propagate() is called whenever the domain
        of this variable changes.
        We say that a change event occurs.
        'c': the constraint for which the Constraint propagate() method
        should be called on change events of this variable.
        """

    @abc.abstractmethod
    def propagate_on_fix(self, c: "constraint.Constraint") -> "None":
        """Asks that Constraint propagate() is called whenever the domain
        of this variable is reduced to a singleton.
        In such a state the variable is fixed, and we say that a fix
        event occurs.
        'c': the constraint for which the Constraint propagate() method
        should be called on fix events of this variable.
        """

    @abc.abstractmethod
    def propagate_on_bound_change(self, c: "constraint.Constraint") -> "None":
        """Asks that Constraint propagate() is called whenever the bound
        (maximum or minimum values) of the domain of this variable changes.
        We say that a bound change event occurs in this case.
        'c': the constraint for which the Constraint propagate() method
        should be called on bound change events of this variable.
        """

    @abc.abstractmethod
    def min(self) -> "int":
        """Returns the minimum of the domain of the variable."""

    @abc.abstractmethod
    def max(self) -> "int":
        """Returns the maximum of the domain of the variable."""

    @abc.abstractmethod
    def size(self) -> "int":
        """Returns the size of the domain of the variable."""

    @abc.abstractmethod
    def fill_array(self, dest: "list[int]") -> "int":
        """Copies the values of the domain into an array.
        'dest': an array large enough {len(dest) >= size()}
        Returns the size of the domain and dest[0,...,size-1] contains the values
        in the domain in an arbitrary order.
        """

    @abc.abstractmethod
    def is_fixed(self) -> "bool":
        """Returns true if the domain of the variable has a single value."""

    @abc.abstractmethod
    def contains(self, v: "int") -> "bool":
        """Returns true if the domain contains the specified value."""

    @abc.abstractmethod
    def remove(self, v: "int") -> "None":
        """Removes the specified value.
        Raises InconsistencyException if the domain becomes empty.
        """

    @abc.abstractmethod
    def fix(self, v: "int") -> "None":
        """Fix the specified value.
        Raises InconsistencyException if the value is not in the domain.
        """

    @abc.abstractmethod
    def remove_below(self, v: "int") -> "None":
        """Remove all the values less than a given value.
        Raises InconsistencyException if the domain becomes empty.
        """

    @abc.abstractmethod
    def remove_above(self, v: "int") -> "None":
        """Remove all the values above a given value.
        Raises InconsistencyException if the domain becomes empty.
        """


class BoolVar(IntVar):
    """Boolean variable interface, that can be used as a 0-1 IntVar
    0 corresponds to false, and 1 corresponds to true.
    """

    @abc.abstractmethod
    def is_true(self) -> "bool":
        """Tests if the variable is fixed to true.
        Returns true if the variable is fixed to true (value 1).
        """

    @abc.abstractmethod
    def is_false(self) -> "bool":
        """Tests if the variable is fixed to false.
        Returns true if the variable is fixed to false (value 0).
        """

    @abc.abstractmethod
    def fix(self, b: "bool" = None, v: "int" = None) -> "None":
        """Use either fix(bool b) or fix(int v).
        Assigns the variable.
        'b': the value to assign to this boolean variable.
        Raises InconsistencyException if the value is not in the domain.
        """


class _DomainListener(domain.DomainListener):
    def __init__(self, int_var_impl: "IntVarImpl"):
        self._int_var_impl: "IntVarImpl" = int_var_impl

    def empty(self) -> "None":
        # Integer vars cannot be empty
        raise exceptions.InconsistencyException()

    def fix(self) -> "None":
        self._schedule_all(self._int_var_impl._on_fix)

    def change(self) -> "None":
        self._schedule_all(self._int_var_impl._on_domain)

    def change_min(self) -> "None":
        self._schedule_all(self._int_var_impl._on_bound)

    def change_max(self) -> "None":
        self._schedule_all(self._int_var_impl._on_bound)

    def _schedule_all(self, constraints: "state.StateStack") -> "None":
        cp = self._int_var_impl._cp
        for i in range(constraints.size()):
            cp.schedule(constraints.get(i))


class IntVarImpl(IntVar):
    """Implementation of a variable with a SparseSetDomain."""

    def __init__(
        self,
        cp: "solver.Solver",
        min: "int" = None,
        max: "int" = None,
        n: "int" = None,
        values: "set[int]" = None,
    ):
        """Creates a variable with the elements as initial domain.

        if values is not None (min, max, n are None), domain: {values}
        if n is not None domain (values, min, max are None): {0,...,n-1}
        if min, max are not None (values, n are None): domain: {min,...,max}
        """
        if (values is not None) and (n is None) and (min is None) and (max is None):
            raise NotImplementedError()
        elif (n is not None) and (min is None) and (max is None) and (values is None):
            min = 0
            max = n - 1
        elif (
            (min is not None) and (max is not None) and (n is None) and (values is None)
        ):
            pass
        else:
            raise ValueError("Incorrect values provided")

        if min == _MIN_VALUE or max == _MAX_VALUE:
            raise ValueError("Consider reducing the domains")
        if min > max:
            raise ValueError("At least one set_value in the domain")
        self._cp: solver.Solver = cp
        self._domain: domain.IntDomain = domain.SparseSetDomain(
            cp.get_state_manager(), min, max
        )
        self._on_domain: state.StateStack = state.StateStack(cp.get_state_manager())
        self._on_fix: state.StateStack = state.StateStack(cp.get_state_manager())
        self._on_bound: state.StateStack = state.StateStack(cp.get_state_manager())
        self._dom_listener: domain.DomainListener = _DomainListener(self)

    def get_solver(self) -> "solver.Solver":
        return self._cp

    def is_fixed(self) -> "bool":
        return self._domain.is_singleton()

    def __str__(self) -> "str":
        return str(self._domain)

    def when_fixed(self, f: "Callable[[], None]") -> "None":
        self._on_fix.push(self._constraint_closure(f))

    def when_bound_change(self, f: "Callable[[], None]") -> "None":
        self._on_bound.push(self._constraint_closure(f))

    def when_domain_change(self, f: "Callable[[], None]") -> "None":
        self._on_domain.push(self._constraint_closure(f))

    def _constraint_closure(self, f: "Callable[[], None]") -> "constraint.Constraint":
        c = constraint.ConstraintClosure(self._cp, f)
        self.get_solver().post(c, False)
        return c

    def propagate_on_domain_change(self, c: "constraint.Constraint") -> "None":
        self._on_domain.push(c)

    def propagate_on_fix(self, c: "constraint.Constraint") -> "None":
        self._on_fix.push(c)

    def propagate_on_bound_change(self, c: "constraint.Constraint") -> "None":
        self._on_bound.push(c)

    def min(self) -> "int":
        return self._domain.min()

    def max(self) -> "int":
        return self._domain.max()

    def size(self) -> "int":
        return self._domain.size()

    def fill_array(self, dest: "list[int]") -> "int":
        return self._domain.fill_array(dest)

    def contains(self, v: "int") -> "bool":
        return self._domain.contains(v)

    def remove(self, v: "int") -> "None":
        self._domain.remove(v, self._dom_listener)

    def fix(self, v: "int") -> "None":
        self._domain.remove_all_but(v, self._dom_listener)

    def remove_below(self, v: "int") -> "None":
        self._domain.remove_below(v, self._dom_listener)

    def remove_above(self, v: "int") -> "None":
        self._domain.remove_above(v, self._dom_listener)


class IntVarViewMul(IntVar):
    """A view on a variable of type {a*x}"""

    def __init__(self, x: "IntVar", a: "int"):
        if (1 + x.min()) * a <= _MIN_VALUE:
            raise OverflowError(
                "Consider applying a smaller mul cte "
                "as the min domain on this "
                "view is <= Integer.MIN_VALUE "
            )
        if (1 + x.max()) * a >= _MAX_VALUE:
            raise OverflowError(
                "Consider applying a smaller mul "
                "cte as the max domain on this view "
                "is >= Integer.MAX _VALUE"
            )

        self._a: "int" = a
        self._x: "IntVar" = x

    def get_solver(self) -> "solver.Solver":
        return self._x.get_solver()

    def when_fixed(self, f: "Callable[[], None]") -> "None":
        self._x.when_fixed(f)

    def when_bound_change(self, f: "Callable[[], None]") -> "None":
        self._x.when_bound_change(f)

    def when_domain_change(self, f: "Callable[[], None]") -> "None":
        self._x.when_domain_change(f)

    def propagate_on_domain_change(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_domain_change(c)

    def propagate_on_fix(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_fix(c)

    def propagate_on_bound_change(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_bound_change(c)

    def min(self) -> "int":
        if self._a >= 0:
            return self._a * self._x.min()
        else:
            return self._a * self._x.max()

    def max(self) -> "int":
        if self._a >= 0:
            return self._a * self._x.max()
        else:
            return self._a * self._x.min()

    def size(self) -> "int":
        return self._x.size()

    def fill_array(self, dest: "list[int]") -> "int":
        s = self._x.fill_array(dest)
        for i in range(s):
            dest[i] *= self._a
        return s

    def is_fixed(self) -> "bool":
        return self._x.is_fixed()

    def contains(self, v: "int") -> "bool":
        if v % self._a != 0:
            return False
        else:
            return self._x.contains(int(v / self._a))

    def remove(self, v: "int") -> "None":
        if v % self._a == 0:
            self._x.remove(int(v / self._a))

    def fix(self, v: "int") -> "None":
        if v % self._a == 0:
            self._x.fix(int(v / self._a))
        else:
            raise exceptions.InconsistencyException()

    def remove_below(self, v: "int") -> "None":
        self._x.remove_below(self._ceil_div(v, self._a))

    def remove_above(self, v: "int") -> "None":
        self._x.remove_above(self._floor_div(v, self._a))

    def _floor_div(self, a: "int", b: "int") -> "int":
        q = a / b
        if a < 0 and q * b != a:
            return int(q - 1)
        else:
            return int(q)

    def _ceil_div(self, a: "int", b: "int") -> "int":
        q = a / b
        if a > 0 and q * b != a:
            return int(q + 1)
        else:
            return int(q)

    def __str__(self) -> "str":
        b = ["{"]
        for i in range(self.min(), self.max()):
            if self.contains(i):
                b.append(f"{i},")
        if self.size() > 0:
            b.append(f"{self.max()}")
        b.append("}")
        return "".join(b)


class IntVarViewOffset(IntVar):
    """A view on a variable of type {x+o}"""

    def __init__(self, x: "IntVar", offset: "int"):
        # y = x + o
        if 0 + x.min() + offset <= _MIN_VALUE:
            raise OverflowError(
                "Consider applying a smaller offset as "
                "the min domain on this view is <= Integer.MIN_VALUE"
            )
        if 0 + x.max() + offset >= _MAX_VALUE:
            raise OverflowError(
                "Consider applying a smaller offset as "
                "the max domain on this view is >= Integer.MAX_VALUE"
            )

        self._x: "IntVar" = x
        self._o: "int" = offset

    def get_solver(self) -> "solver.Solver":
        return self._x.get_solver()

    def when_fixed(self, f: "Callable[[], None]") -> "None":
        self._x.when_fixed(f)

    def when_bound_change(self, f: "Callable[[], None]") -> "None":
        self._x.when_bound_change(f)

    def when_domain_change(self, f: "Callable[[], None]") -> "None":
        self._x.when_domain_change(f)

    def propagate_on_domain_change(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_domain_change(c)

    def propagate_on_fix(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_fix(c)

    def propagate_on_bound_change(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_bound_change(c)

    def min(self) -> "int":
        return self._x.min() + self._o

    def max(self) -> "int":
        return self._x.max() + self._o

    def size(self) -> "int":
        return self._x.size()

    def fill_array(self, dest: "list[int]") -> "int":
        s = self._x.fill_array(dest)
        for i in range(s):
            dest[i] += self._o
        return s

    def is_fixed(self) -> "bool":
        return self._x.is_fixed()

    def contains(self, v: "int") -> "bool":
        return self._x.contains(v - self._o)

    def remove(self, v: "int") -> "None":
        self._x.remove(v - self._o)

    def fix(self, v: "int") -> "None":
        self._x.fix(v - self._o)

    def remove_below(self, v: "int") -> "None":
        self._x.remove_below(v - self._o)

    def remove_above(self, v: "int") -> "None":
        self._x.remove_above(v - self._o)

    def __str__(self) -> "str":
        b = ["{"]
        for i in range(self.min(), self.max()):
            if self.contains(i):
                b.append(f"{i},")
        if self.size() > 0:
            b.append(f"{self.max()}")
        b.append("}")
        return "".join(b)


class IntVarViewOpposite(IntVar):
    """A view on a variable of type {-x}"""

    def __init__(self, x: "IntVar"):
        self._x: "IntVar" = x

    def get_solver(self) -> "solver.Solver":
        return self._x.get_solver()

    def when_fixed(self, f: "Callable[[], None]") -> "None":
        self._x.when_fixed(f)

    def when_bound_change(self, f: "Callable[[], None]") -> "None":
        self._x.when_bound_change(f)

    def when_domain_change(self, f: "Callable[[], None]") -> "None":
        self._x.when_domain_change(f)

    def propagate_on_domain_change(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_domain_change(c)

    def propagate_on_fix(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_fix(c)

    def propagate_on_bound_change(self, c: "constraint.Constraint") -> "None":
        self._x.propagate_on_bound_change(c)

    def min(self) -> "int":
        return -self._x.max()

    def max(self) -> "int":
        return -self._x.min()

    def size(self) -> "int":
        return self._x.size()

    def fill_array(self, dest: "list[int]") -> "int":
        s = self._x.fill_array(dest)
        for i in range(s):
            dest[i] = -dest[i]
        return s

    def is_fixed(self) -> "bool":
        return self._x.is_fixed()

    def contains(self, v: "int") -> "bool":
        return self._x.contains(-v)

    def remove(self, v: "int") -> "None":
        self._x.remove(-v)

    def fix(self, v: "int") -> "None":
        self._x.fix(-v)

    def remove_below(self, v: "int") -> "None":
        self._x.remove_above(-v)

    def remove_above(self, v: "int") -> "None":
        self._x.remove_below(-v)

    def __str__(self) -> "str":
        b = ["{"]
        for i in range(self.min(), self.max()):
            if self.contains(i):
                b.append(f"{i},")
        if self.size() > 0:
            b.append(f"{self.max()}")
        b.append("}")
        return "".join(b)


class BoolVarImpl(BoolVar):
    def __init__(self, binary_var: "IntVar" = None, cp: "solver.Solver" = None):
        if (cp is not None) and (binary_var is None):
            binary_var = IntVarImpl(cp, 0, 1)
        elif (binary_var is not None) and (cp is None):
            # Create a boolean variable view from the binary variable
            if binary_var.max() > 1 or binary_var.min() < 0:
                raise ValueError("Must be a binary {0, 1} variable")
        else:
            raise ValueError("Incorrect values provided")
        self._binary_var: "IntVar" = binary_var

    def is_true(self) -> "bool":
        return self.min() == 1

    def is_false(self) -> "bool":
        return self.max() == 0

    def fix(self, b: "bool" = None, v: "int" = None) -> "None":
        assert v is not None or b is not None
        if v is not None:
            assert b is None
            self._binary_var.fix(v)
            return

        if b:
            self._binary_var.fix(1)
        else:
            self._binary_var.fix(0)

    def get_solver(self) -> "solver.Solver":
        return self._binary_var.get_solver()

    def when_fixed(self, f: "Callable[[], None]") -> "None":
        self._binary_var.when_fixed(f)

    def when_bound_change(self, f: "Callable[[], None]") -> "None":
        self._binary_var.when_bound_change(f)

    def when_domain_change(self, f: "Callable[[], None]") -> "None":
        self._binary_var.when_domain_change(f)

    def propagate_on_domain_change(self, c: "constraint.Constraint") -> "None":
        self._binary_var.propagate_on_domain_change(c)

    def propagate_on_fix(self, c: "constraint.Constraint") -> "None":
        self._binary_var.propagate_on_fix(c)

    def propagate_on_bound_change(self, c: "constraint.Constraint") -> "None":
        self._binary_var.propagate_on_bound_change(c)

    def min(self) -> "int":
        return self._binary_var.min()

    def max(self) -> "int":
        return self._binary_var.max()

    def size(self) -> "int":
        return self._binary_var.size()

    def fill_array(self, dest: "list[int]") -> "int":
        return self._binary_var.fill_array(dest)

    def is_fixed(self) -> "bool":
        return self._binary_var.is_fixed()

    def contains(self, v: "int") -> "bool":
        return self._binary_var.contains(v)

    def remove(self, v: "int") -> "None":
        self._binary_var.remove(v)

    def remove_below(self, v: "int") -> "None":
        self._binary_var.remove_below(v)

    def remove_above(self, v: "int") -> "None":
        self._binary_var.remove_above(v)

    def __str__(self) -> "str":
        if self.is_true():
            return "true"
        elif self.is_false():
            return "false"
        else:
            return "{false,true}"


class BoolVarIsEqual(IntVarImpl, BoolVar):
    def __init__(self, x: "IntVar", v: "int"):
        super().__init__(x.get_solver(), 0, 1)

        if not x.contains(v):
            self.fix(False)
        elif x.is_fixed() and x.min() == v:
            self.fix(True)
        else:
            self.when_fixed(lambda: x.fix(v) if self.is_true() else x.remove(v))
            x.when_domain_change(lambda: self.fix(False) if not x.contains(v) else None)
            x.when_fixed(lambda: self.fix(True) if x.min() == v else self.fix(False))

    def is_true(self) -> "bool":
        return self.min() == 1

    def is_false(self) -> "bool":
        return self.max() == 0

    def fix(self, b: "bool" = None, v: "int" = None) -> "None":
        assert v is not None or b is not None
        if v is not None:
            assert b is None
            super().fix(v)
            return

        if b:
            super().fix(1)
        else:
            super().fix(0)
