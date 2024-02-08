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
from typing import Callable

from mini_cp.cp import factory
from mini_cp.engine import constraint, exceptions, int_var, search, state


class Solver(abc.ABC):
    """Interface for solver."""

    @abc.abstractmethod
    def post(
        self,
        c: "constraint.Constraint" = None,
        enforce_fix_point: "bool" = True,
        b: "int_var.BoolVar" = None,
    ) -> "None":
        """Use either post(BoolVar b) or post(Constraint c, bool enforce_fix_point)
        or post(Constraint c).

        If using post(Constraint, bool):
        Posts the constraint, that calls Constraint post()
        and optionally computes the fix-point.

        If using post(Constraint):
        Posts the constraint that calls Constraint post()
        and computes the fix-point.

        If using post(BoolVar):
        'b': the variable must be set to true
        Forces the boolean variable to be true and
        then computes the fix-point.

        A InconsistencyException is raised if by posting the
        constraint, it is proven that there is no solution.
        """

    @abc.abstractmethod
    def schedule(self, c: "constraint.Constraint") -> "None":
        """Schedules the constraint to be propagated by the fix-point."""

    @abc.abstractmethod
    def fix_point(self) -> "None":
        """Computes the fix-point with all the scheduled constraints."""

    @abc.abstractmethod
    def get_state_manager(self) -> "state.StateManager":
        """Returns the state manager in charge of the global state of the
        solver.
        """

    @abc.abstractmethod
    def on_fix_point(self, listener: "Callable[[], None]") -> "None":
        """Adds a listener called whenever the fix-point.
        'listener' is called whenever the fix point.
        """

    @abc.abstractmethod
    def minimize(self, x: "int_var.IntVar") -> "search.Objective":
        """Creates a minimization objective on the given variable.
        'x': the variable to minimize
        Returns an objective that can minimize x
        See search.DFSearch optimize(Objective).
        """

    @abc.abstractmethod
    def maximize(self, x: "int_var.IntVar") -> "search.Objective":
        """Creates a maximization objective on the given variable.
        'x': the variable to minimize
        Returns an objective that can maximize x
        See search.DFSearch optimize(Objective).
        """


class MiniCP(Solver):
    def __init__(self, sm: "state.StateManager"):
        self._sm: "state.StateManager" = sm
        self._vars: "state.StateStack" = state.StateStack(sm)
        self._propagation_queue: "collections.deque[constraint.Constraint]" = (
            collections.deque()
        )
        self._fix_point_listeners: "list[Callable[[], None]]" = []

    def get_state_manager(self) -> "state.StateManager":
        return self._sm

    def schedule(self, c: "constraint.Constraint") -> "None":
        if c.is_active() and not c.is_scheduled():
            c.set_scheduled(True)
            self._propagation_queue.append(c)

    def on_fix_point(self, listener: "Callable[[], None]") -> "None":
        self._fix_point_listeners.append(listener)

    def _notify_fix_point(self) -> "None":
        for listener in self._fix_point_listeners:
            listener()

    def fix_point(self) -> "None":
        try:
            self._notify_fix_point()
            while self._propagation_queue:
                self._propagate(self._propagation_queue.popleft())
        except exceptions.InconsistencyException as e:
            # empty the queue and unset the scheduled status
            while self._propagation_queue:
                self._propagation_queue.popleft().set_scheduled(False)
            raise e

    def _propagate(self, c: "constraint.Constraint") -> "None":
        c.set_scheduled(False)
        if c.is_active():
            c.propagate()

    def minimize(self, x: "int_var.IntVar") -> "search.Objective":
        return search.Minimize(x)

    def maximize(self, x: "int_var.IntVar") -> "search.Objective":
        return self.minimize(factory.minus(x))

    def post(
        self,
        c: "constraint.Constraint" = None,
        enforce_fix_point: "bool" = True,
        b: "int_var.BoolVar" = None,
    ) -> "None":
        assert (b is not None) or (c is not None)

        if b is not None:
            assert c is None
            b.fix(True)
            self.fix_point()
            return

        c.post()
        if enforce_fix_point:
            self.fix_point()

    def __str__(self) -> "str":
        return f"MiniCP({self._sm})"
