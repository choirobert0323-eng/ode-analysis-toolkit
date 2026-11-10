"""Discrete moving frames for nonzero, non-collinear velocities."""
from core.vector import Vector

class FrenetFrame:
    def __init__(self, T: Vector, N: Vector, B: Vector):
        self.T, self.N, self.B = T, N, B

    def __repr__(self):
        return f"FrenetFrame(T={self.T}, N={self.N}, B={self.B})"

def compute_frenet(prev_v: Vector, curr_v: Vector) -> FrenetFrame:
    if len(prev_v) != 3 or len(curr_v) != 3:
        raise ValueError("Frenet frames require 3D vectors")
    tangent = curr_v.normalized()
    delta = tangent - prev_v.normalized()
    normal_component = delta + tangent * (-delta.dot(tangent))
    if normal_component.norm() < 1e-12:
        raise ValueError("Frenet normal is undefined for locally straight motion")
    normal = normal_component.normalized()
    return FrenetFrame(tangent, normal, tangent.cross(normal).normalized())
