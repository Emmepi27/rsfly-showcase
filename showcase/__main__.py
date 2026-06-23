"""End-to-end demo: synthetic IGC -> 3D track points -> GeoJSON.

Run from the repo root:

    python -m showcase
"""
import json

from . import parse_igc, track_to_geojson

SAMPLE_IGC = [
    "HFDTEDATE:120625,01",
    "B1101355206343N00006198WA0058700558",
    "B1101455206400N00006300WA0059500566",
    "B1101555206460N00006420WA0060300574",
]


def main() -> None:
    points = parse_igc(SAMPLE_IGC)
    feature = track_to_geojson(points, {"name": "demo flight"})
    print(f"Parsed {len(points)} track points (UTC, midnight-safe).")
    print(json.dumps(feature, indent=2))


if __name__ == "__main__":
    main()
