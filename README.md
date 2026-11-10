# ODE Analysis Toolkit

**Rule-based first-order ODE exploration and small numerical simulation examples.**  
Python · SymPy · NumPy · pandas

미분방정식의 구조를 분석하고 수치 계산과 기하학적 좌표 변환을 실험하는 Python 프로젝트입니다.

## Why this project

A differential equation can satisfy several useful descriptions at once. This toolkit extracts basic properties and shows the rules behind candidate classifications, rather than presenting a single unexplained label.

## Features

- Parse local expressions such as `y' = x*y`, `dy/dx = y*(1-y)` and implicit equations.
- Detect derivative order and analyze explicit first-order equations for linearity, autonomy and separability.
- Rank matching taxonomy entries using transparent rule scores.
- Advance position and velocity with an explicit Euler solver.
- Construct discrete moving frames for non-collinear velocities and transform vectors between Cartesian and frame coordinates.

## Quick start

Tested with **Python 3.13** on macOS. From the repository root:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze.py "y' = x*y"
python simulate.py
```

The analysis example reports order 1, `linear: True` and `autonomous: False`. The simulation writes CSV-style coordinates; at t=1 the constant-velocity example reaches (1, 0.5, 0).

No original Excel file is required. `examples/taxonomy.csv` is a newly prepared, minimal taxonomy using standard mathematical forms. An optional CSV/XLSX file can be supplied with `--taxonomy`; required columns are `ID`, `Name`, and `Canonical_Form`.

## Design

| Module | Responsibility |
| --- | --- |
| `core/ode_analyzer.py` | Parsing, structural checks and rule-based taxonomy matching |
| `core/vector.py`, `core/state.py` | Numerical vector and state operations |
| `solver/` | Solver interface and Euler integration |
| `geometry/` | Moving frames, coordinate transforms and finite-difference estimates |
| `analyze.py`, `simulate.py` | Reproducible command-line examples |

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Eight checks cover equation classification, separable coefficients, higher-order labeling, constant-velocity integration, coordinate round trips and undefined straight-line normals. The two command-line examples were also executed during release preparation.

## Limitations

- This is a heuristic exploration tool, not a general symbolic ODE solver. Rule scores are not probabilities or accuracy measurements.
- First-order classification is the supported analysis scope. Higher-order notation is recognized up to order 6, without higher-order classification.
- Enter **trusted local mathematical expressions only**: the CLI uses SymPy expression parsing and is not suitable as an untrusted public input service.
- Euler integration has time-step error. Discrete geometry estimates depend on sampling; Frenet normals are undefined for locally straight motion or zero velocity.
- Experimental noisy/perturbed dynamics from other local versions are not included in this curated release.

## Portfolio summary

Built a Python prototype that inspects first-order ODE structure, explains candidate classes using explicit rules, and separates state, solver and geometry components for reproducible numerical experiments.

## Status and provenance

Portfolio prototype, prepared from a local project. See [PROVENANCE.md](PROVENANCE.md) for release preparation and attribution notes. Original private datasets, environments and unverified media are excluded. Dependency licenses apply separately. A project license has not yet been selected.
