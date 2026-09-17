"""Generate coverage badge data and download badge asset for GitHub Actions."""

import json
import urllib.request
from pathlib import Path


def get_badge_color(percentage: float) -> str:
    """Determine the Shields.io badge color based on coverage percentage.

    Args:
        percentage: The code coverage percentage.

    Returns:
        The color name corresponding to the coverage threshold.
    """
    if percentage >= 95:
        return "brightgreen"
    if percentage >= 90:
        return "green"
    if percentage >= 80:
        return "yellowgreen"
    if percentage >= 70:
        return "yellow"
    if percentage >= 60:
        return "orange"
    return "red"


def generate_badge_files(
    coverage_file: str | Path = "coverage.json",
    output_dir: str | Path = "badges",
) -> None:
    """Read coverage report, create Shields endpoint JSON, and fetch SVG badge.

    Args:
        coverage_file: Path to the JSON coverage report produced by pytest-cov.
        output_dir: Directory where the badge files will be saved.
    """
    cov_path = Path(coverage_file)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with cov_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    percent_str = data["totals"]["percent_covered_display"]
    percentage = float(percent_str)
    color = get_badge_color(percentage)

    endpoint_data = {
        "schemaVersion": 1,
        "label": "coverage",
        "message": f"{percent_str}%",
        "color": color,
    }

    json_dest = out_dir / "coverage.json"
    with json_dest.open("w", encoding="utf-8") as f:
        json.dump(endpoint_data, f, indent=2)

    url = f"https://img.shields.io/badge/coverage-{percent_str}%25-{color}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    svg_dest = out_dir / "coverage.svg"
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            svg_dest.write_bytes(resp.read())
    except Exception as exc:  # noqa: BLE001
        print(f"Warning: unable to fetch SVG badge from {url}: {exc}")


if __name__ == "__main__":
    generate_badge_files()
