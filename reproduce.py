"""Reproduce the selected four-panel Figure 6 and verify its four numerical grids."""
import argparse
import csv
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT = Path(__file__).resolve().parent


def verify_grids(output):
    for letter in "ABCD":
        name = f"selected_panel_{letter}.csv"
        with (ROOT / "references" / name).open(newline="") as f:
            expected = list(csv.reader(f))
        with (output / name).open(newline="") as f:
            actual = list(csv.reader(f))
        if expected[0] != actual[0] or len(expected) != len(actual):
            raise RuntimeError(f"Grid headers or shape differ: {name}")
        e = np.asarray(expected[1:], dtype=float)
        a = np.asarray(actual[1:], dtype=float)
        if not np.allclose(e, a, rtol=1e-10, atol=1e-10):
            raise RuntimeError(f"Grid values differ: {name}")
        print(f"PASS numerical reference: panel {letter}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "unittest", "-v", "test_figure6"],
                   cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/generate_figure6.py"),
                    "--output-dir", str(output)], cwd=ROOT, check=True)
    verify_grids(output)
    versions = {"python": platform.python_version(),
                "packages": {name: importlib.metadata.version(name)
                             for name in ["numpy", "reportlab", "pypdfium2"]},
                "validation": "four numerical references; rtol=atol=1e-10",
                "analysis": "generic parameter sweeps; no empirical calibration"}
    (output / "software_versions.json").write_text(json.dumps(versions, indent=2) + "\n")
    print(f"Figure 6 reproduction complete: {output}")


if __name__ == "__main__":
    main()
