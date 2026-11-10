# geometry/basis.py
from core.vector import Vector
from geometry.frenet import FrenetFrame

class BasisTransform:
    """
    Handles coordinate transforms between Cartesian and Frenet bases.
    """

    def __init__(self, frame: FrenetFrame):
        self.T = frame.T
        self.N = frame.N
        self.B = frame.B

    def to_frenet(self, v: Vector) -> Vector:
        """
        Cartesian vector -> Frenet coordinates
        """
        return Vector([
            v.dot(self.T),
            v.dot(self.N),
            v.dot(self.B),
        ])

    def to_cartesian(self, coeffs: Vector) -> Vector:
        """
        Frenet coordinates -> Cartesian vector
        """
        a, b, c = coeffs.data
        return (
            self.T * a +
            self.N * b +
            self.B * c
        )
