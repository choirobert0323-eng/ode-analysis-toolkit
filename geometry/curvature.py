# geometry/curvature.py
import math
from core.vector import Vector
from geometry.frenet import FrenetFrame


def curvature(prev_v: Vector, curr_v: Vector, dt: float) -> float:
    """
    Discrete curvature:
        κ = |dT/ds|
    where ds ≈ |v| dt
    """
    if dt <= 0:
        raise ValueError("dt must be positive")
    T_prev = prev_v.normalized()
    T_curr = curr_v.normalized()

    dT = T_curr - T_prev
    ds = curr_v.norm() * dt

    if ds == 0:
        return 0.0

    return dT.norm() / ds


def torsion(prev_frame: FrenetFrame, curr_frame: FrenetFrame, dt: float, speed: float = 1.0) -> float:
    """
    Discrete torsion:
        τ = -dB/ds · N
    """
    if dt <= 0 or speed <= 0:
        raise ValueError("dt and speed must be positive")
    dB = curr_frame.B - prev_frame.B
    ds = dt * speed  # ds ≈ speed * dt; default assumes unit speed

    if ds == 0:
        return 0.0

    return -dB.dot(curr_frame.N) / ds
