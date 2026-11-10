# core/state.py
from core.vector import Vector

class State:
    def __init__(self, x: Vector, v: Vector):
        self.x = x
        self.v = v

    def __add__(self, other):
        return State(self.x + other.x, self.v + other.v)

    def __mul__(self, scalar: float):
        return State(self.x * scalar, self.v * scalar)

    __rmul__ = __mul__
