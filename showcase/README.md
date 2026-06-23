# Showcase excerpts

Illustrative code, rewritten from scratch for this repo — **not** RSFly production code,
and with no secrets, private thresholds or real data. Each file is intentionally small;
the point is correct, tested code that shows how the pieces fit.

- **`igc_parser.py`** — parses IGC `B`-records into ordered 3D track points, handling the
  real-world details: midnight-UTC rollover via the `HFDTE` header, invalid `V` fixes,
  malformed lines, and GPS vs barometric altitude.
- **`geojson_serializer.py`** — turns track points into GeoJSON, the API's wire format,
  honouring the RFC 7946 rule that a `LineString` needs ≥ 2 positions. This serializes the
  *raw* track; public endpoints serve only masked/aggregated geometry
  (see [../ARCHITECTURE.md](../ARCHITECTURE.md#privacy-posture)).
- **`proximity_query.py`** — a standard GeoDjango + PostGIS proximity query, showing the
  `geography`/metres pattern (distances on SRID 4326 come out in degrees).

Run the end-to-end demo (synthetic IGC → track points → GeoJSON) from the repo root:

```bash
python -m showcase
```

Tests live in [`../tests/`](../tests/) — run them with `pytest`.
