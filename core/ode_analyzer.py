# core/ode_analyzer.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

import sympy as sp
import pandas as pd
from pathlib import Path
import re


@dataclass
class ODEMatch:
    id: str
    name: str
    canonical_form: str
    score: int
    why: List[str]


@dataclass
class ODEAnalysis:
    raw: str
    order: int
    linear: Optional[bool]
    autonomous: Optional[bool]
    kind: str  # primary label (separable/linear/autonomous/riccati/...)
    components: Dict[str, Any]
    matches: List[ODEMatch]


class ODEAnalyzer:
    """
    Phase-2 analyzer driven by the Excel taxonomy (FO-001..FO-024).
    """

    def __init__(self, excel_path: str | None = None):
        self.x = sp.Symbol("x", real=True)
        self.y = sp.Symbol("y", real=True)
        self.yp = sp.Symbol("yp", real=True)
        self.derivatives = {1: self.yp, **{n: sp.Symbol(f"y{n}", real=True) for n in range(2, 7)}}

        path = Path(excel_path) if excel_path else Path(__file__).resolve().parents[1] / "examples/taxonomy.csv"
        self.db = pd.read_csv(path) if path.suffix.lower() == ".csv" else pd.read_excel(path)
        required = {"ID", "Name", "Canonical_Form"}
        if not required.issubset(self.db.columns):
            raise ValueError("Taxonomy requires ID, Name and Canonical_Form columns")
        self.db = self.db.fillna("")

        # Quick map
        self.id_to_row = {r["ID"]: r for _, r in self.db.iterrows()}

    # ---------- parsing ----------
    def parse_equation(self, s: str) -> sp.Eq:
        """
        Accepts:
          - "y' = ..."
          - "dy/dx = ..."
          - "... = ..."
          - (implicit) "M(x,y) + N(x,y)*y' = 0"
        """
        text = s.strip().replace("dy/dx", "yp")
        text = re.sub(r"y('+)", lambda m: "yp" if len(m[1]) == 1 else f"y{len(m[1])}", text)
        if not text or text.count("=") > 1:
            raise ValueError("Enter one equation, for example: y' = x*y")
        left, right = text.split("=", 1) if "=" in text else (text, "0")
        local = {"x": self.x, "y": self.y, "yp": self.yp,
                 **{f"y{n}": symbol for n, symbol in self.derivatives.items() if n > 1}}
        # This local CLI accepts trusted mathematical expressions only.
        L, R = sp.sympify(left, locals=local), sp.sympify(right, locals=local)
        if not isinstance(L, sp.Expr) or not isinstance(R, sp.Expr):
            raise ValueError("Both sides must be mathematical expressions")
        return sp.Eq(L, R, evaluate=False)

    def order_of(self, eq: sp.Eq) -> int:
        return max((n for n, symbol in self.derivatives.items()
                    if eq.lhs.has(symbol) or eq.rhs.has(symbol)), default=0)

    def solve_for_yp(self, eq: sp.Eq) -> Optional[sp.Expr]:
        try:
            sol = sp.solve(eq, self.yp, dict=True)
            if not sol:
                return None
            return sp.simplify(sol[0][self.yp])
        except Exception:
            return None

    # ---------- primitive checks ----------
    def is_autonomous(self, F: sp.Expr) -> bool:
        return (self.x not in F.free_symbols)

    def try_separable(self, F: sp.Expr) -> Optional[Tuple[sp.Expr, sp.Expr]]:
        sep = sp.separatevars(F, symbols=[self.x, self.y], dict=True)
        if not sep:
            return None

        fx = sp.simplify(sep.get("coeff", 1) * sep.get(self.x, 1))
        gy = sp.simplify(sep.get(self.y, 1))

        if (self.y in fx.free_symbols) or (self.x in gy.free_symbols):
            return None

        if sp.simplify(F - fx * gy) != 0:
            return None

        return fx, gy

    def try_linear(self, F: sp.Expr) -> Optional[Tuple[sp.Expr, sp.Expr]]:
        # F = A(x)*y + B(x)
        A = sp.diff(F, self.y)
        if self.y in A.free_symbols:
            return None

        B = sp.simplify(F - A * self.y)
        if self.y in B.free_symbols:
            return None

        p = sp.simplify(-A)  # y' + p y = q
        q = sp.simplify(B)
        return p, q

    def poly_in_y_degree(self, F: sp.Expr) -> Optional[int]:
        try:
            P = sp.Poly(F, self.y)
            return int(P.degree())
        except Exception:
            return None

    def depends_only_on_ratio_y_over_x(self, F: sp.Expr) -> bool:
        # Check if F(x, y) can be expressed as G(y/x)
        u = sp.Symbol("u", real=True)
        expr = sp.simplify(F.subs({self.y: u * self.x}))
        return self.x not in expr.free_symbols

    def is_form_G_of_y_over_x(self, F: sp.Expr) -> bool:
        # FO-006 y' = F(y/x)
        if self.x not in F.free_symbols and self.y in F.free_symbols:
            # autonomous is a separate class; this is not ratio-based
            return False
        if (self.x in F.free_symbols) and (self.y in F.free_symbols):
            return self.depends_only_on_ratio_y_over_x(F)
        return False

    def is_form_Gy_over_x(self, F: sp.Expr) -> Optional[sp.Expr]:
        # FO-019: y' = G(y)/x  (i.e., x*y' = G(y))
        if self.x not in F.free_symbols:
            return None
        G = sp.simplify(F * self.x)
        # if resulting depends only on y -> success
        if (self.x not in G.free_symbols) and (self.y in G.free_symbols or G.free_symbols == {self.y} or G.free_symbols == set()):
            return G
        return None

    # ---------- Excel-driven matching ----------
    def match_first_order(self, eq: sp.Eq, F: Optional[sp.Expr], base: ODEAnalysis) -> List[ODEMatch]:
        matches: List[ODEMatch] = []

        def add_match(fid: str, score: int, why: List[str]):
            r = self.id_to_row.get(fid)
            if r is None:
                return
            matches.append(ODEMatch(
                id=fid,
                name=str(r["Name"]),
                canonical_form=str(r["Canonical_Form"]),
                score=score,
                why=why
            ))

        if base.order != 1:
            return matches

        # If solvable for y' (explicit)
        if F is not None:
            # FO-023: solvable for y' (generic explicit)
            add_match("FO-023", 10, ["Equation solvable for y' (explicit form)"])

            # FO-009: autonomous y' = f(y)
            if base.autonomous:
                add_match("FO-009", 60, ["F does not depend on x (autonomous)"])

            # FO-001: separable y' = f(x) g(y)
            if "f(x)" in base.components and "g(y)" in base.components:
                add_match("FO-001", 80, ["F(x,y) separable into f(x)*g(y)"])

            # FO-006: homogeneous y' = F(y/x)
            if self.is_form_G_of_y_over_x(F):
                add_match("FO-006", 70, ["F depends only on y/x (homogeneous)"])

            # FO-002/012/013: linear
            if base.linear is True and "p(x)" in base.components and "q(x)" in base.components:
                p = base.components["p(x)"]
                q = base.components["q(x)"]
                add_match("FO-002", 75, ["First-order linear: y' + p(x)*y = q(x)"])
                if sp.simplify(q) == 0:
                    add_match("FO-012", 85, ["Homogeneous linear: q(x)=0"])
                else:
                    add_match("FO-013", 85, ["Nonhomogeneous linear: q(x)≠0"])

            # FO-005 Riccati / FO-016 Abel by polynomial degree in y
            deg = self.poly_in_y_degree(F)
            if deg == 2:
                add_match("FO-005", 65, ["Polynomial in y of degree 2 (Riccati candidate)"])
            elif deg == 3:
                add_match("FO-016", 65, ["Polynomial in y of degree 3 (Abel candidate)"])

            # FO-018 Emden–Fowler: y' = x^a y^b  (monomial)
            # Check if separable into x-only and y-only monomials
            sep = self.try_separable(F)
            if sep is not None:
                fx, gy = sep
                # heuristic: if fx is power of x and gy is power of y (or constant)
                if fx.is_Pow or fx == self.x or fx.free_symbols == {self.x}:
                    if gy.is_Pow or gy == self.y or gy.free_symbols == {self.y} or gy.free_symbols == set():
                        add_match("FO-018", 45, ["Separable with power-like factors (Emden–Fowler candidate)"])

            # FO-019 Cauchy-type: x*y' = f(y)
            Gy = self.is_form_Gy_over_x(F)
            if Gy is not None:
                add_match("FO-019", 55, ["x*y' = f(y) (Cauchy-type)"])

            # FO-010 Logistic: y' = a*y*(1 - y/K)  (heuristic via quadratic with factor y)
            # Detect if F is quadratic and factorable as c*y*(A - B*y)
            if deg == 2:
                fac = sp.factor(F)
                # if y is a factor
                if sp.simplify(F.subs(self.y, 0)) == 0:
                    add_match("FO-010", 35, ["Quadratic with factor y (logistic candidate)"])

            # FO-004 Bernoulli: y' + p(x)*y = q(x)*y^n, n != 1
            # Heuristic: F has exactly two y-powers: y^1 and y^n (n != 1), no constant
            try:
                P = sp.Poly(F, self.y)
                monoms = P.monoms()
                coeffs = P.coeffs()
                # monoms are tuples like (k,) for y^k
                powers = [m[0] for m in monoms]
                if 1 in powers and len(powers) == 2:
                    n = [p for p in powers if p != 1][0]
                    if n not in (0, 1):
                        # constant term absent
                        if 0 not in powers:
                            add_match("FO-004", 55, [f"Two-term polynomial in y with powers 1 and {n} (Bernoulli candidate)"])
            except Exception:
                pass

        else:
            # Not solvable explicitly for y' but still first-order -> FO-015
            add_match("FO-015", 40, ["First-order implicit: F(x,y,y')=0 (not solved for y')"])

        # sort by score desc
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    # ---------- main ----------
    def analyze(self, s: str) -> ODEAnalysis:
        eq = self.parse_equation(s)
        order = self.order_of(eq)

        linear: Optional[bool] = None
        autonomous: Optional[bool] = None
        kind = "unknown"
        comps: Dict[str, Any] = {}
        matches: List[ODEMatch] = []

        if order == 1:
            F = self.solve_for_yp(eq)

            if F is not None:
                autonomous = self.is_autonomous(F)

                sep = self.try_separable(F)
                lin = self.try_linear(F)

                if sep is not None:
                    kind = "separable"
                    comps["f(x)"], comps["g(y)"] = sep

                if lin is not None:
                    linear = True
                    comps["p(x)"], comps["q(x)"] = lin
                    kind = "linear" if kind == "unknown" else kind
                else:
                    linear = False

                if autonomous and kind == "unknown":
                    kind = "autonomous"
                    comps["h(y)"] = F

            # Excel matching
            base = ODEAnalysis(s, order, linear, autonomous, kind, comps, [])
            matches = self.match_first_order(eq, F, base)

        return ODEAnalysis(
            raw=s,
            order=order,
            linear=linear,
            autonomous=autonomous,
            kind=kind,
            components=comps,
            matches=matches,
        )
