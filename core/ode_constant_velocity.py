# core/ode_constant_velocity.py
from .ode import ODE
from .state import State
from .vector import Vector

class ConstantVelocityODE(ODE):
    def derivative(self, state: State, t: float) -> State:
        dx = state.v
        dv = Vector([0.0, 0.0, 0.0])
        return State(dx, dv)
