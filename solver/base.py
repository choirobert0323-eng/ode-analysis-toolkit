# solver/base.py
from abc import ABC, abstractmethod
from core.state import State
from core.ode import ODE

class Solver(ABC):
    """
    Time integration interface.
    Solver advances the system state forward in time.
    """

    def __init__(self, ode: ODE):
        self.ode = ode

    @abstractmethod
    def step(self, state: State, t: float, dt: float) -> State:
        """
        Advance state by one timestep dt.
        """
        pass
