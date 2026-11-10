"""Run a small reproducible constant-velocity example."""
from core.vector import Vector
from core.state import State
from core.ode_constant_velocity import ConstantVelocityODE
from solver.euler import EulerSolver

def main():
    state = State(Vector([0, 0, 0]), Vector([1, 0.5, 0]))
    solver = EulerSolver(ConstantVelocityODE())
    print("t,x,y,z")
    for step in range(11):
        print(f"{step / 10:.1f}," + ",".join(f"{v:.3f}" for v in state.x.data))
        state = solver.step(state, step / 10, 0.1)

if __name__ == "__main__":
    main()
