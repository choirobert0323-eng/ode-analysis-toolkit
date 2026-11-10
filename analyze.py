"""Analyze trusted local mathematical input; no external workbook required."""
import argparse
from core.ode_analyzer import ODEAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Rule-based first-order ODE analyzer")
    parser.add_argument("equation", nargs="?", default="y' = x*y")
    parser.add_argument("--taxonomy", help="Optional CSV/XLSX with ID, Name, Canonical_Form")
    args = parser.parse_args()
    try:
        result = ODEAnalyzer(args.taxonomy).analyze(args.equation)
    except (ValueError, TypeError, SyntaxError) as exc:
        parser.error(str(exc))
    print(f"Equation: {result.raw}")
    print(f"Order: {result.order}; linear: {result.linear}; autonomous: {result.autonomous}")
    print(f"Primary label: {result.kind}")
    for key, value in result.components.items():
        print(f"  {key}: {value}")
    for match in result.matches[:5]:
        print(f"  {match.id}: {match.name} (rule score {match.score})")

if __name__ == "__main__":
    main()
