"""Генерация диаграмм из исходников; сначала выполните npm ci."""
from pathlib import Path
import subprocess


if __name__ == "__main__":
    subprocess.run(
        ["node", "tools/render_diagrams.mjs"],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
    )
