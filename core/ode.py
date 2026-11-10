# core/ode.py
from abc import ABC, abstractmethod
from .state import State

class ODE(ABC):
    @abstractmethod
    def derivative(self, state: State, t: float) -> State:
        """
        Compute d(state)/dt at time t
        """
        pass
