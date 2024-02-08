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
from typing import Callable, Iterable

from mini_cp.cp import factory
from mini_cp.engine import exceptions, int_var, solver, state


class Constraint(abc.ABC):
    """Interface implemented by every constraint."""

    @abc.abstractmethod
    def post(self) -> "None":
        """Initializes the constraint when it is posted to the solver."""

    @abc.abstractmethod
    def propagate(self) -> "None":
        """Propagates the constraint."""

    @abc.abstractmethod
    def set_scheduled(self, scheduled: "bool") -> "None":
        """Set the status of the constraint as scheduled to be propagated
        by the fix-point.
        This method is called by the solver when the constraint
        is enqueued in the propagation queue and is not intended
        to be called by the user.
        'scheduled': a value that is true when the constraint is
        enqueued in the propagation queue, false when dequeued
        """

    @abc.abstractmethod
    def is_scheduled(self) -> "bool":
        """Returns the schedule status in the fix-point."""

    @abc.abstractmethod
    def set_active(self, active: "bool") -> "None":
        """Activates or deactivates the constraint such that it is not
        scheduled anymore.
        Typically, called by the constraint to let the solver know it
        should not be scheduled any more when it is subsumed.
        By default, the constraint is active.
        'active': the status to be set, this state is reversible and unset
        on state restoration (StateManager restore_state())
        """

    @abc.abstractmethod
    def is_active(self) -> "bool":
        """Returns the active status of the constraint.
        Returns the last set value passed to set_active() in this state
        frame (StateManager restore_state())
        """


class AbstractConstraint(Constraint, abc.ABC):
    """Abstract class the most of the constraints should extend."""

    def __init__(self, cp: "solver.Solver"):
        # The solver in which the constraint is created
        self._cp: "solver.Solver" = cp
        self._active: "state.State" = cp.get_state_manager().make_state_ref(True)
        self._scheduled: "bool" = False

    def post(self) -> "None":
        pass

    def get_solver(self) -> "solver.Solver":
        return self._cp

    def propagate(self) -> "None":
        pass

    def set_scheduled(self, scheduled: "bool") -> "None":
        self._scheduled = scheduled

    def is_scheduled(self) -> "bool":
        return self._scheduled

    def set_active(self, active: "bool") -> "None":
        self._active.set_value(active)

    def is_active(self) -> "bool":
        return self._active.value()


class ConstraintClosure(AbstractConstraint):
    def __init__(self, cp: "solver.Solver", filtering: "Callable[[], None]"):
        super().__init__(cp)
        self._filtering: "Callable[[], None]" = filtering

    def post(self) -> "None":
        pass

    def propagate(self) -> "None":
        self._filtering()


class NotEqual(AbstractConstraint):
    """Not Equal constraint between two variables"""

    def __init__(self, x: "int_var.IntVar", y: "int_var.IntVar", v: "int" = 0):
        """Creates a constraint such that {x != y + v}
        'x': the left member
        'y': the right member
        'v': the offset value on y
        See cp.Factory not_equal(IntVar, IntVar, int)
        """
        super().__init__(x.get_solver())
        self._x: "int_var.IntVar" = x
        self._y: "int_var.IntVar" = y
        self._v: "int" = v

    def post(self) -> "None":
        if self._y.is_fixed():
            self._x.remove(self._y.min() + self._v)
        elif self._x.is_fixed():
            self._y.remove(self._x.min() - self._v)
        else:
            self._x.propagate_on_fix(self)
            self._y.propagate_on_fix(self)

    def propagate(self) -> "None":
        if self._y.is_fixed():
            self._x.remove(self._y.min() + self._v)
        else:
            self._y.remove(self._x.min() - self._v)
        self.set_active(False)


class Absolute(AbstractConstraint):
    """Absolute value constraint"""

    def __init__(self, x: "int_var.IntVar", y: "int_var.IntVar"):
        """Creates the absolute value constraint {y = |x|}
        'x': the input variable such that its absolute value is equal
        to y
        'y': the variable that represents the absolute value of x
        """
        super().__init__(x.get_solver())
        self._x: "int_var.IntVar" = x
        self._y: "int_var.IntVar" = y

    def post(self) -> "None":
        # TODO
        raise NotImplementedError("Absolute")

    def propagate(self) -> "None":
        # y = |x|
        # TODO
        raise NotImplementedError("Absolute")


class Maximum(AbstractConstraint):
    """Maximum constraint"""

    def __init__(self, x: "list[int_var.IntVar]", y: "int_var.IntVar"):
        """Creates the maximum constraint y = maximum(x[0],x[1],...,x[n])
        'x': the list of variables on which the maximum is to be found
        'y': the variable that is equal to the maximum on x
        """
        super().__init__(x[0].get_solver())
        assert len(x) > 0
        self._x: "list[int_var.IntVar]" = x
        self._y: "int_var.IntVar" = y

    def post(self) -> "None":
        # TODO
        # - call the constraint on all bound changes for the variables (x.propagateOnBoundChange(this))
        # - call a first time the propagate() method to trigger the propagation
        raise NotImplementedError("Maximum")

    def propagate(self) -> "None":
        # TODO
        # - update the min and max values of each x[i] based on the bounds of y
        # - update the min and max values of each y based on the bounds of all x[i]
        raise NotImplementedError("Maximum")


class Equal(AbstractConstraint):
    """Equal constraint between two variables"""

    def __init__(self, x: "int_var.IntVar", y: "int_var.IntVar"):
        """Creates a constraint such that {x = y}
        'x': the left member
        'y': the right member
        See mini_cp.cp.factory equal(IntVar, IntVar)
        """
        super().__init__(x.get_solver())
        self._x: "int_var.IntVar" = x
        self._y: "int_var.IntVar" = y

    def post(self) -> "None":
        def callback1() -> "None":
            self._bounds_intersect()
            self._prune_equals(self._x, self._y, dom_val)

        def callback2() -> "None":
            self._bounds_intersect()
            self._prune_equals(self._y, self._x, dom_val)

        if self._y.is_fixed():
            self._x.fix(self._y.min())
        elif self._x.is_fixed():
            self._y.fix(self._x.min())
        else:
            self._bounds_intersect()
            dom_val = [0] * max(self._x.size(), self._y.size())
            self._prune_equals(self._y, self._x, dom_val)
            self._prune_equals(self._x, self._y, dom_val)
            self._x.when_domain_change(callback1)
            self._y.when_domain_change(callback2)

    def _prune_equals(
        self, from_: "int_var.IntVar", to: "int_var.IntVar", dom_val: "list[int]"
    ) -> "None":
        """Dom consistent filtering in the direction 'from' -> 'to'
        every value of 'to' has a support in from
        """
        # dumpy the domain of 'to' into 'dom_val'
        n_val = to.fill_array(dom_val)
        for k in range(n_val):
            if not from_.contains(dom_val[k]):
                to.remove(dom_val[k])

    def _bounds_intersect(self) -> "None":
        """Make sure bound of variables are the same"""
        new_min = max(self._x.min(), self._y.min())
        new_max = min(self._x.max(), self._y.max())
        self._x.remove_below(new_min)
        self._x.remove_above(new_max)
        self._y.remove_below(new_min)
        self._y.remove_above(new_max)


class LessOrEqual(AbstractConstraint):
    """Less or equal constraint between two variables"""

    def __init__(self, x: "int_var.IntVar", y: "int_var.IntVar"):
        super().__init__(x.get_solver())
        self._x: "int_var.IntVar" = x
        self._y: "int_var.IntVar" = y

    def post(self) -> "None":
        self._x.propagate_on_bound_change(self)
        self._y.propagate_on_bound_change(self)
        self.propagate()

    def propagate(self) -> "None":
        self._x.remove_above(self._y.max())
        self._y.remove_below(self._x.min())
        if self._x.max() <= self._y.min():
            self.set_active(False)


class IsEqual(AbstractConstraint):
    """Reified equality constraint b <=> x == v
    See mini_cp.cp.factory is_equal(IntVar, int)
    """

    def __init__(self, b: "int_var.BoolVar", x: "int_var.IntVar", v: "int"):
        """Returns a boolean variable representing
        whether one variable is equal to the given constant.
        'x': the variable
        'v': the constant
        'b': the boolean variable that is set to true if and only if
        x takes the value v
        See mini_cp.cp.factory is_equal(IntVar, int)
        """
        super().__init__(b.get_solver())
        self._b: "int_var.BoolVar" = b
        self._x: "int_var.IntVar" = x
        self._v: "int" = v

    def post(self) -> "None":
        self.propagate()
        if self.is_active():
            self._x.propagate_on_domain_change(self)
            self._b.propagate_on_fix(self)

    def propagate(self) -> "None":
        if self._b.is_true():
            self._x.fix(self._v)
            self.set_active(False)
        elif self._b.is_false():
            self._x.remove(self._v)
            self.set_active(False)
        elif not self._x.contains(self._v):
            self._b.fix(False)
            self.set_active(False)
        elif self._x.is_fixed():
            self._b.fix(True)
            self.set_active(False)


class IsLessOrEqual(AbstractConstraint):
    """Reified less or equal constraint b <=> x <= v"""

    def __init__(self, b: "int_var.BoolVar", x: "int_var.IntVar", v: "int"):
        """Creates a constraint that
        link a boolean variable representing
        whether one variable is less or equal to the given constant.
        'b': a boolean variable that is true if and only if
        x takes a value less or equal to v
        'x': a variable
        'v': a constant
        See mini_cp.cp.factory is_less_or_equal(IntVar, int)
        """
        super().__init__(b.get_solver())
        self._b: "int_var.BoolVar" = b
        self._x: "int_var.IntVar" = x
        self._v: "int" = v

    def post(self) -> "None":

        def callback() -> "None":
            # should deactivate the constraint as it is entailed
            if self._b.is_true():
                self._x.remove_above(self._v)
            else:
                self._x.remove_below(self._v + 1)

        def callback2() -> "None":
            if self._x.max() <= self._v:
                # should deactivate the constraint as it is entailed
                self._b.fix(v=1)
            elif self._x.min() > self._v:
                # should deactivate the constraint as it is entailed
                self._b.fix(v=0)

        if self._b.is_true():
            self._x.remove_above(self._v)
        elif self._b.is_false():
            self._x.remove_below(self._v + 1)
        elif self._x.max() <= self._v:
            self._b.fix(v=1)
        elif self._x.min() > self._v:
            self._b.fix(v=0)
        else:
            self._b.when_fixed(callback)
            self._x.when_bound_change(callback2)


class Element1D(AbstractConstraint):
    """Creates an element constraint {array[y] = z}
    'array': the array to index
    'y': the index variable
    'z': the result variable
    """

    def __init__(self, array: "list[int]", y: "int_var.IntVar", z: "int_var.IntVar"):
        super().__init__(y.get_solver())
        self._t: "list[int]" = array

        self._sorted_perm: "list[int]" = [i for i in range(len(array))]
        self._sorted_perm.sort(key=lambda i: self._t[i])

        sm = self.get_solver().get_state_manager()
        self._low: "state.StateInt" = sm.make_state_int(0)
        self._up: "state.StateInt" = sm.make_state_int(len(array) - 1)

        self._y: "int_var.IntVar" = y
        self._z: "int_var.IntVar" = z

    def post(self) -> "None":
        raise NotImplementedError("Element1D")

    def propagate(self) -> "None":
        raise NotImplementedError("Element1D")


class _Triple:

    def __init__(self, x: "int", y: "int", z: "int"):
        self.x: "int" = x
        self.y: "int" = y
        self.z: "int" = z


class Element2D(AbstractConstraint):
    """Element Constraint modeling {matrix[x][y] = z}"""

    def __init__(
        self,
        mat: "list[list[int]]",
        x: "int_var.IntVar",
        y: "int_var.IntVar",
        z: "int_var.IntVar",
    ):
        super().__init__(x.get_solver())
        self._matrix: "list[list[int]]" = mat
        self._x: "int_var.IntVar" = x
        self._y: "int_var.IntVar" = y
        self._z: "int_var.IntVar" = z
        self._n: "int" = len(mat)
        self._m: "int" = len(mat[0])

        self._xyz: "list[_Triple]" = []
        for i in range(len(mat)):
            for j in range(len(mat[i])):
                self._xyz.append(_Triple(i, j, mat[i][j]))

        self._xyz.sort(key=lambda o: o.z)
        sm = self.get_solver().get_state_manager()
        self._low: "state.StateInt" = sm.make_state_int(0)
        self._up: "state.StateInt" = sm.make_state_int(len(self._xyz) - 1)

        self._n_cols_sup: "list[state.StateInt]" = [
            sm.make_state_int(self._m) for _ in range(self._n)
        ]
        self._n_rows_sup: "list[state.StateInt]" = [
            sm.make_state_int(self._n) for _ in range(self._m)
        ]

    def post(self) -> "None":
        self._x.remove_below(0)
        self._x.remove_above(self._n - 1)
        self._y.remove_below(0)
        self._y.remove_above(self._m - 1)
        self._x.propagate_on_domain_change(self)
        self._y.propagate_on_domain_change(self)
        self._z.propagate_on_bound_change(self)
        self.propagate()

    def _update_supports(self, lost_pos: "int") -> "None":
        if self._n_cols_sup[self._xyz[lost_pos].x].decrement() == 0:
            self._x.remove(self._xyz[lost_pos].x)
        if self._n_rows_sup[self._xyz[lost_pos].y].decrement() == 0:
            self._y.remove(self._xyz[lost_pos].y)

    def propagate(self) -> "None":
        l = self._low.value()
        u = self._up.value()
        z_min = self._z.min()
        z_max = self._z.max()

        while (
            self._xyz[l].z < z_min
            or not self._x.contains(self._xyz[l].x)
            or not self._y.contains(self._xyz[l].y)
        ):
            self._update_supports(l)
            l += 1
            if l > u:
                raise exceptions.InconsistencyException()

        while (
            self._xyz[u].z > z_max
            or not self._x.contains(self._xyz[u].x)
            or not self._y.contains(self._xyz[u].y)
        ):
            self._update_supports(u)
            u -= 1
            if l > u:
                raise exceptions.InconsistencyException()

        self._z.remove_below(self._xyz[l].z)
        self._z.remove_above(self._xyz[u].z)
        self._low.set_value(l)
        self._up.set_value(u)


class Sum(AbstractConstraint):
    """Sum Constraint"""

    def __init__(
        self, x: "list[int_var.IntVar]", y: "int_var.IntVar" = None, v: "int" = None
    ):
        """Creates a sum constraint.

        If 'y' is not None (and 'v' is None):
        This constraint holds iff
        {x[0]+x[1]+...+x[len(x)-1] == y}
        'x': the non-empty left hand side of the sum
        'y': variable, the right hand side of the sum

        Elif 'v' is not None (and 'y' is None):
        This constraint holds iff
        {x[0]+x[1]+...+x[len(x)-1] == y}
        'x': the non-empty left hand side of the sum
        'v': value, the right hand side of the sum
        """
        super().__init__(x[0].get_solver())
        self._x: "list[int_var.IntVar]" = [var for var in x]

        if y is not None and v is None:
            self._x.append(factory.minus(y))
        elif v is not None and y is None:
            self._x.append(factory.make_int_var(self.get_solver(), -v, -v))
        else:
            raise ValueError("Incorrect values provided")

        self._n: "int" = len(self._x)
        self._min: "list[int]" = [0] * len(self._x)
        self._max: "list[int]" = [0] * len(self._x)

        self._n_fixed: "state.StateInt" = (
            self.get_solver().get_state_manager().make_state_int(0)
        )
        self._sum_fixed: "state.StateInt" = (
            self.get_solver().get_state_manager().make_state_int(0)
        )
        self._fixed: "list[int]" = [i for i in range(self._n)]

    def post(self) -> "None":
        for var in self._x:
            var.propagate_on_bound_change(self)
        self.propagate()

    def propagate(self) -> "None":
        # Filter the unfixed vars and update the partial sum
        nf = self._n_fixed.value()
        sum_min = self._sum_fixed.value()
        sum_max = self._sum_fixed.value()
        # Iterate over not-fixed variables and update partial sum
        # if one variable is detected as fixed
        for i in range(nf, len(self._x)):
            idx = self._fixed[i]
            self._min[idx] = self._x[idx].min()
            self._max[idx] = self._x[idx].max()
            # Update partial sum
            sum_min += self._min[idx]
            sum_max += self._max[idx]
            if self._x[idx].is_fixed():
                self._sum_fixed.set_value(self._sum_fixed.value() + self._x[idx].min())
                # Swap the variables
                self._fixed[i] = self._fixed[nf]
                self._fixed[nf] = idx
                nf += 1

        self._n_fixed.set_value(nf)
        if sum_min > 0 or sum_max < 0:
            raise exceptions.InconsistencyException()

        # Iterate over not-fixed variables
        for i in range(nf, len(self._x)):
            idx = self._fixed[i]
            self._x[idx].remove_above(-(sum_min - self._min[idx]))
            self._x[idx].remove_below(-(sum_max - self._max[idx]))


class AllDifferentBinary(AbstractConstraint):
    """AllDifferent Constraint"""

    def __init__(self, x: "list[int_var.IntVar]"):
        super().__init__(x[0].get_solver())
        self._x: "list[int_var.IntVar]" = x

    def post(self) -> "None":
        cp = self._x[0].get_solver()
        for i in range(len(self._x)):
            for j in range(i + 1, len(self._x)):
                cp.post(NotEqual(self._x[i], self._x[j]), False)


class Graph(abc.ABC):
    """Directed graph API"""

    def n(self) -> "int":
        """Returns the number of nodes in this graph.
        Nodes are identified from 0 to n() - 1
        """

    def in_(self, id: "int") -> "Iterable[int]":
        """Returns the incoming node indices in the specified node
        'id': the identified of the specified node
        Returns the identifiers of the nodes pointing to the specified node
        """

    def out(self, id: "int") -> "Iterable[int]":
        """Returns the outgoing node indices from the specified node
        'id': the identifier of the specified node
        Returns the identifiers of the nodes originating from the specified node
        """


def transpose(graph: "Graph") -> "Graph":
    """Transpose the graph i.e. every edge is reversed.
    'graph': a graph
    Returns a new graph such that every edge is reversed
    """
    # TODO


def strongly_connected_components(graph: "Graph") -> "list[int]":
    """Computes the strongly connected components of the graph
    'graph': the input graph on which to compute the strongly
    connected components
    Returns for each node id, an id of the strongly connected
    components it belongs to
    """
    # TODO


def dfs_node(
    graph: "Graph",
    action: "Callable[[bool, int],None]",
    visited: "list[int]",
    start: "int",
) -> "None":
    # TODO
    pass


def path_exists(graph: "Graph", start: "int", end: "int") -> "bool":
    """Checks if a path exists between start and end
    'graph': a graph
    'start': a node id from the graph
    'end': a node if from the graph
    Returns true if a directed path from start to end exists, false otherwise
    """
    # TODO


class MaximumMatching:
    """Compute and Maintain a Maximum Matching
    in the variable-value graph
    """

    # TODO


class AllDifferentDC(AbstractConstraint):
    """Arc Consistent AllDifferent Constraint

    Algorithm described in
    "A filtering algorithm for constraints of difference in CSPs"
    J-C. Régin, AAAI-94
    """

    # TODO

    def __init__(self, x: "list[int_var.IntVar]"):
        super().__init__(x[0].get_solver())
        raise NotImplementedError("AllDifferentDC")

    def post(self) -> "None":
        raise NotImplementedError("AllDifferentDC")

    def propagate(self) -> "None":
        raise NotImplementedError("AllDifferentDC")


class AllDifferentFWC(AbstractConstraint):
    """Forward Checking filtering AllDifferent Constraint

    Whenever one variable is fixed, this value
    is removed from the domain of other variables.
    This filtering is weaker than the AllDifferentDC
    but executes faster.
    """

    # TODO
    def __init__(self, x: "list[int_var.IntVar]"):
        super().__init__(x[0].get_solver())
        self._x: "list[int_var.IntVar]" = x
        raise NotImplementedError("AllDifferentFWC")


class Circuit(AbstractConstraint):
    """Hamiltonian Circuit Constraint with a successor model"""

    # TODO

    def __init__(self, x: "list[int_var.IntVar]"):
        super().__init__(x[0].get_solver())
        raise NotImplementedError("Circuit")


class Profile:
    """Representation of a cumulated Profile
    data structure as a contiguous sequence of Rectangle
    built from a set of Rectangle using a sweep-line algorithm
    """

    # TODO


class Cumulative(AbstractConstraint):
    """Cumulative constraint with timetable filtering"""

    # TODO

    def __init__(
        self,
        start: "list[int_var.IntVar]",
        duration: "list[int]",
        requirement: "list[int]",
        capa: "int",
        post_mirror: "bool",
    ):
        super().__init__(start[0].get_solver())
        raise NotImplementedError("Cumulative")


class CumulativeDecomposition(AbstractConstraint):
    """Cumulative constraint with sum decomposition (very slow)."""

    # TODO

    def __init__(
        self,
        start: "list[int_var.IntVar]",
        duration: "list[int]",
        demand: "list[int]",
        capa: "int",
    ):
        super().__init__(start[0].get_solver())
        raise NotImplementedError("CumulativeDecomposition")


class ThetaTree:
    """Data structure described in
    Global Constraints in Scheduling, 2008 Petr Vilim, PhD thesis
    See http://vilim.eu/petr/disertace.pdf The thesis
    """

    # TODO


class Disjunctive(AbstractConstraint):
    """Disjunctive Scheduling Constraint:
    Any two pairs of activities cannot overlap in time.
    """

    # TODO

    def __init__(
        self, start: "list[int_var.IntVar]", duration: "list[int]", post_mirror: "bool"
    ):
        super().__init__(start[0].get_solver())
        raise NotImplementedError("Disjunctive")


class DisjunctiveBinary(AbstractConstraint):
    """Constraint enforcing that two activities cannot overlap in time

    The implementation of this constraint uses reified constraints.
    """

    # TODO

    def __init__(
        self,
        start1: "int_var.IntVar",
        duration1: "int",
        start2: "int_var.IntVar",
        duration2: "int",
    ):
        super().__init__(start1.get_solver())
        raise NotImplementedError("DisjunctiveBinary")


class Element1DDomainConsistent(AbstractConstraint):
    """Element Constraint modeling {array[y] = z}"""

    # TODO

    def __init__(self, array: "list[int]", y: "int_var.IntVar", z: "int_var.IntVar"):
        super().__init__(y.get_solver())
        raise NotImplementedError("Element1DDomainConsistent")


class Element1DVar(AbstractConstraint):

    # TODO

    def __init__(self, array: "list[int]", y: "int_var.IntVar", z: "int_var.IntVar"):
        super().__init__(y.get_solver())
        raise NotImplementedError("Element1DVar")


class IsLessOrEqualVar(AbstractConstraint):
    """Reified is less or equal constraint {b <=> x <= y}"""

    # TODO
    def __init__(self, b: "int_var.BoolVar", x: "int_var.IntVar", y: "int_var.IntVar"):
        super().__init__(x.get_solver())
        raise NotImplementedError("IsLessOrEqualVar")


class IsOr(AbstractConstraint):
    """Reified logical or constraint"""

    # TODO
    def __init__(self, b: "int_var.BoolVar", x: "list[int_var.BoolVar]"):
        super().__init__(b.get_solver())
        raise NotImplementedError("IsOr")


class Or(AbstractConstraint):
    """Logical or constraint {x1 or x2 or ... xn}"""

    # TODO

    def __init__(self, x: "list[int_var.BoolVar]"):
        super().__init__(x[0].get_solver())
        raise NotImplementedError("Or")


class TableCT(AbstractConstraint):
    """Implementation of Compact Table algorithm described in
    Compact-Table: Efficiently Filtering Table Constraints with Reversible Sparse Bit-Sets
    Jordan Demeulenaere, Renaud Hartert, Christophe Lecoutre, Guillaume Perez, Laurent Perron, Jean-Charles Régin,
    Pierre Schaus
    See https://www.info.ucl.ac.be/~pschaus/assets/publi/cp2016-compacttable.pdf The article
    """

    # TODO
    def __init__(self, x: "list[int_var.IntVar]", table: "list[list[int]]"):
        super().__init__(x[0].get_solver())
        raise NotImplementedError("TableCT")


class TableDecomp(AbstractConstraint):

    # TODO

    def __init__(self, x: "list[int_var.IntVar]", table: "list[list[int]]"):
        super().__init__(x[0].get_solver())
        raise NotImplementedError("TableDecomp")
