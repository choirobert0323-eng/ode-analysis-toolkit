# solver/euler.py
from solver.base import Solver
from core.state import State

class EulerSolver(Solver):
    """
    Explicit Euler time integrator.
    """

    def step(self, state: State, t: float, dt: float) -> State:
        deriv = self.ode.derivative(state, t)
        return state + deriv * dt
