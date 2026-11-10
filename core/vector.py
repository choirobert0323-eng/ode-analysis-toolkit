# core/vector.py
import numpy as np

class Vector:
    def __init__(self, data):
        self.data = np.array(data, dtype=float)

    def __add__(self, other):
        return Vector(self.data + other.data)

    def __sub__(self, other):
        return Vector(self.data - other.data)

    def __mul__(self, scalar: float):
        return Vector(self.data * scalar)

    __rmul__ = __mul__

    def norm(self):
        return np.linalg.norm(self.data)

    def normalized(self):
        n = self.norm()
        if n == 0:
            raise ValueError("Cannot normalize zero vector")
        return Vector(self.data / n)

    def dot(self, other):
        return float(np.dot(self.data, other.data))

    def cross(self, other):
        return Vector(np.cross(self.data, other.data))

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"Vector({self.data})"
