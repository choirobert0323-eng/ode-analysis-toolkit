import numpy as np
import pytest
from core.ode_analyzer import ODEAnalyzer
from core.vector import Vector
from core.state import State
from core.ode_constant_velocity import ConstantVelocityODE
from geometry.frenet import compute_frenet
from geometry.basis import BasisTransform
from solver.euler import EulerSolver

@pytest.mark.parametrize("equation,linear,autonomous", [
    ("y' = x*y", True, False),
    ("dy/dx = y*(1-y)", False, True),
    ("y' + 2*y = x", True, False),
])
def test_classification(equation, linear, autonomous):
    result = ODEAnalyzer().analyze(equation)
    assert result.order == 1
    assert result.linear is linear
    assert result.autonomous is autonomous
    assert result.matches

def test_separation_preserves_coefficient():
    result = ODEAnalyzer().analyze("y' = 2*x*y")
    assert "f(x)" in result.components
    assert result.components["f(x)"] * result.components["g(y)"] == 2 * ODEAnalyzer().x * ODEAnalyzer().y

def test_second_order_is_not_mislabeled():
    result = ODEAnalyzer().analyze("y'' + y = 0")
    assert result.order == 2
    assert result.matches == []

def test_euler_constant_velocity():
    initial = State(Vector([0, 0, 0]), Vector([1, 2, 3]))
    actual = EulerSolver(ConstantVelocityODE()).step(initial, 0, 0.5)
    np.testing.assert_allclose(actual.x.data, [0.5, 1, 1.5])
    np.testing.assert_allclose(actual.v.data, [1, 2, 3])

def test_frame_round_trip():
    frame = compute_frenet(Vector([1, 0, 0]), Vector([1, 0.1, 0]))
    transform = BasisTransform(frame)
    value = Vector([2, -3, 4])
    np.testing.assert_allclose(transform.to_cartesian(transform.to_frenet(value)).data, value.data, atol=1e-12)

def test_straight_motion_has_no_frenet_normal():
    with pytest.raises(ValueError, match="straight"):
        compute_frenet(Vector([1, 0, 0]), Vector([2, 0, 0]))
