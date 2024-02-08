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

 Factory to create {Solver}, {IntVar}, {Constraint}
 and some modeling utility methods.
 Example for the n-queens problem:

 cp = factory.make_solver(False)
 q = factory.make_int_var_array(cp, n, n)
 for i in range(n):
    for j in range(n):
        cp.post(factory.not_equal(q[i], q[j]))
        cp.post(factory.not_equal(q[i], q[j], j - 1))
        cp.post(factory.not_equal(q[i], q[j], i - j))

 search = factory.make_dfs(cp, branching_scheme.first_fail(q))
 search.on_solution(lambda: print("solution", str(q)))
 stats = search.solve()
"""

from typing import Callable

from mini_cp.engine import constraint, int_var, search, solver, state

_MAX_VALUE = 2147483647
_MIN_VALUE = -2147483648


def make_solver(by_copy: "bool" = False) -> "solver.Solver":
    """Creates a constraint programming solver
    'by_copy': a value that should be true to specify copy-based
    state management or false for a trail-based memory management
    Returns a constraint programming solver
    """
    if by_copy:
        return solver.MiniCP(state.Copier())
    else:
        return solver.MiniCP(state.Trailer())


def make_int_var(
    cp: "solver.Solver",
    min: "int" = None,
    max: "int" = None,
    sz: "int" = None,
    values: "set[int]" = None,
) -> "int_var.IntVar":
    """If 'sz' is not None ('min', 'max', 'values' are None):
    Creates a variable with a domain of specified arity.
    'cp': the solver in which the variable is created
    'sz': a positive value that is the size of the domain
    Returns a variable with domain equal to the set {0,...,sz-1}

    Elif 'min', 'max' are not  None ('sz', 'values' are None):
    'cp': the solver in which the variable is created
    'min': the lower bound of the domain (included)
    'max': the upper bound of the domain (included) {max > min}
    Returns a variable with domain equal to the set {min,...,max}

    Elif 'values' is not None ('sz', 'min', 'max' are None):
    'cp': the solver in which the variable is created
    'values': a set of values
    Returns a variable with domain equal to the set of values
    """
    return int_var.IntVarImpl(cp, min, max, sz, values)


def make_bool_var(cp: "solver.Solver") -> "int_var.BoolVar":
    """Creates a boolean variable.
    'cp': the solver in which the variable is created
    Returns an un-instantiated boolean variable
    """
    return int_var.BoolVarImpl(cp=cp)


def make_int_var_array(
    cp: "solver.Solver",
    n: "int",
    sz: "int" = None,
    min: "int" = None,
    max: "int" = None,
    body: "Callable[[int], int_var.IntVar]" = None,
) -> "list[int_var.IntVar]":
    """If 'body' is not None ('sz', 'min', 'max' are None):
    Creates an array of variables with specified function.
    'cp': the solver in which the variables are created
    'n': the number of variables to create
    'body': the function that given the index i in the array creates/map the
    corresponding IntVar
    Returns an array of n variables with variable at index i generated
    as body(i).

    Elif 'sz' is not None ('body', 'min', 'max' are None):
    'cp': the solver in which the variables are created
    'n': the number of variables to create
    'sz': a positive value that is the size of the domain
    Returns an array of n variables, each with domain equal to the set
    {0,...,sz-1}.

    Elif 'min', 'max' are not None ('body', 'sz' are None):
    'cp': the solver in which the variables are created
    'n': the number of variables to create
    'min': the lower bound of the domain (included)
    'max': the upper bound of the domain (included) {max > min}
    Returns an array of n variables each with a domain equal to the set
    {min,...,max}.
    """
    if (body is not None) and (sz is None) and (min is None) and (max is None):
        return _make_int_var_array(n, body)
    elif (sz is not None) and (body is None) and (min is None) and (max is None):
        return _make_int_var_array(n, lambda i: make_int_var(cp, sz=sz))
    elif (min is not None) and (max is not None) and (body is None) and (sz is None):
        return _make_int_var_array(n, lambda i: make_int_var(cp, min, max))
    else:
        raise ValueError("Incorrect values provided")


def _make_int_var_array(
    n: "int", body: "Callable[[int], int_var.IntVar]"
) -> "list[int_var.IntVar]":
    """Creates an array of variables with specified function
    'n': the number of variables to create
    'body': the function that given the index i in the array creates/map the
    corresponding IntVar
    Returns an array of n variables with variable at index i generated
    as body(i)
    """
    t = []
    for i in range(n):
        t.append(body(i))
    return t


def make_dfs(
    cp: "solver.Solver", branching: "Callable[[], list[Callable[[], None]]]"
) -> "search.DFSearch":
    """Creates a Depth First Search with custom branching heuristic

    Example of binary search: At each node it selects
    the first free variable qi from the array q,
    and creates two branches qi!=v where v is the min value domain
    def callback() -> "list[Callable[[], None]]":
        qi = None
        for i in range(len(q)):
            if q[i].size() > 1:
                qi = q[i]
                break
        if qi == None:
            return _EMPTY
        else:
            v = qi.min()
            left = lambda: cp.post(factory.equal(qi, v)) # left branch
            right = lambda: cp.post(factory.not_equal(qi, v)) # right branch
            return [left, right]

    search = factory.make_dfs(cp, callback)

    'cp': the depth first search object ready to execute with
    DFSearch solve() or DFSearch optimize(Objective)
    using the given branching scheme
    See first_fail(list[IntVar])
    """
    return search.DFSearch(cp.get_state_manager(), branching)


# -------------- constraints -----------------------


def mul(x: "int_var.IntVar", a: "int") -> "int_var.IntVar":
    """A variable that is a view of {x*a}
    'x': a variable
    'a': a constant to multiply x with
    Returns a variable that is a view of {x*a}
    """
    if a == 0:
        return make_int_var(x.get_solver(), 0, 0)
    elif a == 1:
        return x
    elif a < 0:
        return minus(int_var.IntVarViewMul(x, -a))
    else:
        return int_var.IntVarViewMul(x, a)


def minus(x: "int_var.IntVar", v: "int" = None) -> "int_var.IntVar":
    """If v is None:
    A variable that is a view of {-x}
    'x': a variable
    Returns a variable that is a view of {-x}

    Else:
    A variable that is a view of {x-v}
    'v': a value
    Returns a variable that is a view of {x-v}
    """
    if v is None:
        return int_var.IntVarViewOpposite(x)
    else:
        if v == 0:
            return x
        else:
            return int_var.IntVarViewOffset(x, -v)


def plus(x: "int_var", v: "int") -> "int_var.IntVar":
    """A variable that is a view of {x+v}
    'x': a variable
    'v': a value
    Returns a variable that is a view of {x+v}
    """
    if v == 0:
        return x
    else:
        return int_var.IntVarViewOffset(x, v)


def Not(b: "int_var.BoolVar") -> "int_var.BoolVar":
    """A boolean variable that is a view of {!b}
    'b': a boolean variable
    Returns a boolean variable that is a view of {!b}
    """
    return int_var.BoolVarImpl(plus(minus(b), 1))


def absolute(x: "int_var.IntVar") -> "int_var.IntVar":
    """Computes a variable that is the absolute value of the given variable.
    This relation is enforced by the Absolute constraint posted
    by calling this method.
    'x': a variable
    Returns a variable that represents the absolute value of x
    """
    if x.min() >= 0:
        return x
    else:
        r = make_int_var(x.get_solver(), 0, max(-x.min(), x.max()))
        x.get_solver().post(constraint.Absolute(x, r))
        return r


def maximum(x: "list[int_var.IntVar]") -> "int_var.IntVar":
    """Computes a variable that is the maximum of a set of variables.
    This relation is enforced by the Maximum constraint
    posted by calling this method.
    'x': the list of variables on which to compute the maximum
    Returns a variable that represents the maximum on x.
    See factory minimum(list[IntVar])
    """
    cp = x[0].get_solver()
    min_val = min([var.min() for var in x])
    max_val = max([var.max() for var in x])
    y = make_int_var(cp, min_val, max_val)
    cp.post(constraint.Maximum(x, y))
    return y


def minimum(x: "list[int_var.IntVar]") -> "int_var.IntVar":
    """Computes a variable that is the minimum of a set of variables.
    This relation is enforced by the Maximum constraint posted
    by calling this method.
    'x': the variables on which to compute the minimum
    Returns a variable that represents the minimum on x.
    See factory maximum(list[IntVar])
    """
    minus_x = [minus(var) for var in x]
    return minus(maximum(minus_x))


def equal(
    x: "int_var.IntVar", v: "int" = None, y: "int_var.IntVar" = None
) -> "constraint.Constraint":
    """If v is not None (and y is None):
    Returns a constraint imposing that the variable is
    equal to some given value.
    'x': a variable
    'v': a value
    Returns a constraint so that {x = v}

    Elif y is not None (and v is None):
    Returns a constraint imposing that the two different variables
    must take the value.
    'x': a variable
    'y': a variable
    Returns a constraint so that {x = y}
    """
    if (v is not None) and (y is None):

        class EqualConstraint(constraint.AbstractConstraint):
            def __init__(self, cp: "solver.Solver"):
                super().__init__(cp)

            def post(self) -> "None":
                x.fix(v)

        return EqualConstraint(x.get_solver())

    elif (y is not None) and (v is None):
        return constraint.Equal(x, y)
    else:
        raise ValueError("Only v or y has to be None")


def less_or_equal(
    x: "int_var.IntVar", v: "int" = None, y: "int_var.IntVar" = None
) -> "constraint.Constraint":
    """If v is not None (and y is None):
    Returns a constraint imposing that the variable less or
    equal to some given value.
    'x': the variable that is constrained to be less or equal to v
    'v': the value that must be the upper bound on x
    Returns a constraint so that {x <= v}

    Elif y is not None (and v is None):
    Returns a constraint imposing that the
    first variable is less or equal to the second one.
    'x': a variable
    'y': a variable
    Returns a constraint so that {x <= y}
    """
    if (v is not None) and (y is None):

        class LessOrEqualConstraint(constraint.AbstractConstraint):
            def __init__(self, cp: "solver.Solver"):
                super().__init__(cp)

            def post(self) -> "None":
                x.remove_above(v)

        return LessOrEqualConstraint(x.get_solver())

    elif (y is not None) and (v is None):
        return constraint.LessOrEqual(x, y)
    else:
        raise ValueError("Only v or y has to be None")


def larger_or_equal(
    x: "int_var.IntVar", v: "int" = None, y: "int_var.IntVar" = None
) -> "constraint.Constraint":
    """If v is not None (and y is None):
    Returns a constraint imposing that the variable larger of
    equal to some given value.
    'x': the variable that is constrained to be larger or equal to v
    'v': the value that must be the lower bound on x
    Returns a constraint so that {x >= v}

    Elif y is not None (and v is None):
    'x': a variable
    'y': a variable
    Returns a constraint so that {x >= y}
    """
    if (v is not None) and (y is None):

        class LargerOrEqualConstraint(constraint.AbstractConstraint):
            def __init__(self, cp: "solver.Solver"):
                super().__init__(cp)

            def post(self) -> "None":
                x.remove_below(v)

        return LargerOrEqualConstraint(x.get_solver())

    elif (y is not None) and (v is None):
        return constraint.LessOrEqual(y, x)
    else:
        raise ValueError("Only v or y has to be None")


def not_equal(
    x: "int_var.IntVar", y: "int_var.IntVar" = None, v: "int" = 0
) -> "constraint.Constraint":
    """If 'y' is not None:
    'x': a variable
    'y': a variable
    'v': a constant
    Returns a constraint so that {x != y + v}.
    Else:
    'x': the variable that is constrained to be different from v
    'v': the value that must be different from x
    Returns a constraint so that {x != v}.
    """
    if y is not None:
        return constraint.NotEqual(x, y, v)
    else:

        class NotEqualConstraint(constraint.AbstractConstraint):
            def __init__(self, cp: "solver.Solver"):
                super().__init__(cp)

            def post(self) -> "None":
                x.remove(v)

        return NotEqualConstraint(x.get_solver())


def is_equal(x: "int_var.IntVar", c: "int") -> "int_var.BoolVar":
    """Returns a boolean variable representing
    whether one variable is equal to te given constant.
    This relation is enforced by the IsEqual constraint
    posted by calling this method.
    'x': the variable
    'c': the constant
    Returns a boolean variable that is true if and only if x takes the
    value c
    See IsEqual
    """
    b = make_bool_var(x.get_solver())
    cp = x.get_solver()
    cp.post(constraint.IsEqual(b, x, c))
    return b


def is_less_or_equal(x: "int_var.IntVar", c: "int") -> "int_var.BoolVar":
    """Returns a boolean variable representing
    whether one variable is less or equal to the given constant.
    This relation is enforced by the IsLessOrEqual constraint
    posted by calling this method.
    'x': the variable
    'c': the constant
    Returns a boolean variable that is true if and only if x takes
    a value less or equal to c
    """
    b = make_bool_var(x.get_solver())
    cp = x.get_solver()
    cp.post(constraint.IsLessOrEqual(b, x, c))
    return b


def is_less(x: "int_var.IntVar", c: "int") -> "int_var.BoolVar":
    """Returns a boolean variable representing
    whether one variable is less than the given constant.
    This relation is enforced by the IsLessOrEqual constraint
    posted by calling this method.
    'x': the variable
    'c': the constant
    Returns a boolean variable that is true if and only if x
    takes a value less than c
    """
    return is_less_or_equal(x, c - 1)


def is_larger_or_equal(x: "int_var.IntVar", c: "int") -> "int_var.BoolVar":
    """Returns a boolean variable representing
    whether one variable is larger or equal to the given constant.
    This relation is enforced by the IsLessOrEqual constraint
    posted by calling this method.
    'x': the variable
    'c': the constant
    Returns a boolean variable that is true if and only if
    x takes a value larger or equal to c
    """
    return is_less_or_equal(minus(x), -c)


def is_larger(x: "int_var.IntVar", c: "int") -> "int_var.BoolVar":
    """Returns a boolean variable representing
    whether one variable is larger than the given constant.
    This relation is enforced by the IsLessOrEqual constraint
    posted by calling this method.
    'x': the variable
    'c': the constant
    Returns a boolean variable that is true if and only if
    x takes a value larger than c
    """
    return is_larger_or_equal(x, c + 1)


def element_1d(array: "list[int]", y: "int_var.IntVar") -> "int_var.IntVar":
    """Returns a variable representing
    the value in an array at the position
    specified by the given index variable
    This relation is enforced by the Element1D constraint
    posted by calling this method.
    'array': the array of values
    'y': the variable
    Returns a variable equal to {array[y]}
    """
    cp = y.get_solver()
    z = make_int_var(cp, min(array), max(array))
    cp.post(constraint.Element1D(array, y, z))
    return z


def element_2d(
    matrix: "list[list[int]]", x: "int_var.IntVar", y: "int_var.IntVar"
) -> "int_var.IntVar":
    """Returns a variable representing
    the value in a matrix at the position
    specified by the two given row and column index variables
    This relation is enforced by the Element2D constraint
    posted by calling this method.
    'matrix': the n x m 2D array of values
    'x': the row variable with domain included in 0...n-1
    'y': the column variable with domain included in 0...m-1
    Returns a variable equal to {matrix[x][y]}
    """
    min_val = _MAX_VALUE
    max_val = _MIN_VALUE
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            min_val = min(min_val, matrix[i][j])
            max_val = max(max_val, matrix[i][j])

    z = make_int_var(x.get_solver(), min_val, max_val)
    x.get_solver().post(constraint.Element2D(matrix, x, y, z))
    return z


def sum_var(x: "list[int_var.IntVar]") -> "int_var.IntVar":
    """Returns a variable representing
    the sum of a given set of variables.
    This relation is enforced by the Sum constraint
    posted by calling this method.
    'x': the n variables to sum
    Returns a variable equal to {x[0]+x[1]+...+x[n-1]}
    """
    sum_min = 0
    sum_max = 0
    for i in range(len(x)):
        sum_min += x[i].min()
        sum_max += x[i].max()

    if sum_min < _MIN_VALUE or sum_max > _MAX_VALUE:
        raise OverflowError(
            "Domains are too large for sum constraint "
            "and would exceed Integer bounds"
        )

    cp = x[0].get_solver()
    s = make_int_var(cp, sum_min, sum_max)
    cp.post(constraint.Sum(x, s))
    return s


def Sum(
    x: "list[int_var.IntVar]", y: "int_var.IntVar" = None, v: "int" = None
) -> "constraint.Constraint":
    """If 'y' is not None (and 'v' is None):
    Returns a sum constraint.
    'x': an array of variables
    'y': a variable
    Returns a constraint so that {y = x[0]+x[1]+...+x[n-1]}

    Elif 'v' is not None (and 'y' is None):
    Returns a sum constraint
    'x': an array of variables
    'v': a constant
    Returns a constraint so that {v = x[0]+x[1]+...+x[n-1]}
    """
    return constraint.Sum(x, y, v)


def all_different(x: "list[int_var.IntVar]") -> "constraint.Constraint":
    """Returns a binary decomposition of the AllDifferent constraint.
    'x': an array of variables
    Returns a constraint so that {x[i] != x[j] for all i < j}
    """
    return constraint.AllDifferentBinary(x)


def all_different_dc(x: "list[int_var.IntVar]") -> "constraint.Constraint":
    """Returns an AllDifferent constrain that enforces
    domain consistency.
    'x': an array of variables
    Returns a constraint so that {x[i] != x[j] for all i < j}
    """
    return constraint.AllDifferentDC(x)
