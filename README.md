# MiniCP (Python) - Constraint Programming Solver


## Table of Contents

*   [About MiniCP](#about-minicp)
*   [Code map](#code-map)
*   [Quick Start](#quick-start)
*   [Other](#other)


## About MiniCP

*   MiniCP is an open-source Constraint Programming Solver for 
    solving optimization and satisfaction problems.
*   MiniCP technical documentation, exercises, etc. 
    can be found at http://minicp.org
*   This code is a translation of the original code written in Java.
*   Original code in java: https://github.com/minicp/minicp
*   Online course on how this solver works: https://www.edx.org/learn/computer-programming/universite-catholique-de-louvain-constraint-programming


## Code map

*   [mini_cp](mini_cp) Root directory for source code.
    *   [cp](mini_cp/cp) Factory methods for modeling.
    *   [engine](mini_cp/engine) Constraint solver.
    *   [examples](mini_cp/examples) Python examples.
    *   [tests](mini_cp/tests) Unit tests.


## Quick Start

You may look at code [examples](mini_cp/examples). To run `n_queens` example
from terminal, run `python -m mini_cp.examples.n_queens`


## Other

*   Python 3.8 or above is required
*   To run tests, install [pytest](https://pytest.org/) and run `pytest` in the terminal
*   Code is formatted using [black](https://pypi.org/project/black/)
