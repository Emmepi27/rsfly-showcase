# RSFly — Public Showcase

> Production Web-GIS platform for free-flight (paragliding): IGC processing, 3D geospatial storage, and 2D/3D flight replay.

**Live:** https://rsfly.app  ·  **Status:** in production since late April 2026 · designed, built and operated solo

![CI](https://github.com/Emmepi27/rsfly-showcase/actions/workflows/ci.yml/badge.svg)

## See it

RSFly lets paraglider pilots upload their flight logs (**IGC** files), stores each track as a
**3D geospatial geometry**, analyses it, and replays the flight on an interactive 2D/3D map with a
timeline.

<!-- Demo media (sample data only — never real user flights). Add to assets/ and uncomment. -->
<!-- ![RSFly 3D flight replay (demo data)](assets/replay-3d-demo.gif) -->
<!-- ![RSFly 2D map replay (demo data)](assets/replay-2d-demo.png) -->

> **Demo screenshots / replay GIF:** in [`assets/`](assets/) (sample data only).

## My role

**Founder and sole engineer** — product architecture and end-to-end implementation: the PostGIS
spatial data model, the IGC processing pipeline, the REST / GeoJSON APIs, the Nuxt/Vue frontend, and
the 2D/3D replay.

## Timeline

- **2022** — started as an experimental bachelor's thesis at the University of Rome Tor Vergata, from
  a blank data model (begun at 21).
- **2022–2025** — continued solo development on the same codebase alongside university; B.A. defended
  December 2025, final grade **103/110**, thesis defended in **German**.
- **April 2026** — public production launch at [rsfly.app](https://rsfly.app).
- **June 2026** — 143 registered users, 193 uploaded flights, 3,832 flight views.

Four years of sustained, mostly solo work — thesis, a full-time foreign-language degree, and earlier
jobs in parallel.

## Architecture at a glance

```
IGC upload → parsing → PostGIS 3D geometries → async analysis → GeoJSON/JSON API → 2D/3D replay
```

See **[ARCHITECTURE.md](ARCHITECTURE.md)** for the data-flow and component diagrams.

## Stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Django, **GeoDjango**, Django REST Framework |
| Spatial DB | PostgreSQL + **PostGIS** |
| Async processing | Celery + Redis |
| Frontend | Nuxt 4, Vue 3, TypeScript |
| Maps & 3D | **MapLibre GL**, **deck.gl**, **Three.js** |
| Infrastructure | Docker |

## Engineering decisions & trade-offs

- **A real 3D spatial model, not flat JSON.** Tracks are stored as true 3D geometries (PostGIS
  `LineString` / `Point` with elevation, SRID 4326), so spatial queries — proximity, bounding boxes,
  indexed lookups — run in the database, not in application code.
- **Flight-data privacy as a design constraint.** Flight tracks reveal home launch sites and routines,
  so public surfaces never serve raw IGC; launch/landing points are coarsened and shared views
  aggregated. See [ARCHITECTURE.md](ARCHITECTURE.md#privacy-posture).
- **Open-source mapping.** MapLibre GL rather than a proprietary SDK, to control tile cost and avoid
  lock-in.
- **Async-first processing.** Heavier post-flight analysis runs on a Celery worker so uploads stay
  responsive.

## What was hard

- **IGC is a messy real-world format.** Manufacturer extensions, invalid (`V`) GPS fixes, GPS-vs-
  barometric altitude, and times that roll over midnight UTC — the parser has to survive all of it
  without dropping a flight. The excerpt in [`showcase/`](showcase/) shows the shape of this.
- **Querying 3D tracks efficiently.** Storing geometries in PostGIS means respecting the classic trap
  that distances on SRID 4326 are in *degrees*, not metres — proximity uses the `geography` type so
  `ST_DWithin` works in metres.
- **A smooth 3D replay in the browser** with thousands of fixes per flight (track simplification /
  level of detail).
- **Privacy by construction**, designed in from the start rather than bolted on.

## Quality

The production codebase has unit / integration tests (pytest). The excerpts in
[`showcase/`](showcase/) ship with their own tests ([`tests/`](tests/)) and a runnable demo
(`python -m showcase`); CI runs lint + tests on every push.

## Traction (dated snapshot)

As of **June 2026** — ~2 months in production, after ~4 years of development since 2022:

- **143** registered users
- **193** uploaded flights
- **3,832** flight views

_A point-in-time snapshot, not independently audited._

## What's in this repo

> The production source code is **private**. This repository documents the architecture and includes
> illustrative excerpts rewritten from scratch — no production code, secrets, or real flight data.

| File / folder | What it is |
| --- | --- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Data-flow and component diagrams (Mermaid) |
| [`showcase/`](showcase/) | IGC parser, GeoJSON serializer, GeoDjango proximity query + runnable demo |
| [`tests/`](tests/) | Tests for the excerpts |
| [`.env.example`](.env.example) | Placeholder configuration (no real values) |
| [`assets/`](assets/) | Demo screenshots (sample data only) |
| [`LICENSE`](LICENSE) | MIT |

## Origin

Experimental B.A. thesis — *"RSFly: progettazione di un'applicazione web per la gestione di dati di
volo libero e visualizzazione geospaziale"* — Information Society and Foreign Languages, University of
Rome Tor Vergata, supervisor **Prof. Luca Allulli**, defended in German.

## Contact

**Manuel Pammer** — manuelpamm@gmail.com · [manudesign.it](https://manudesign.it) · [github.com/Emmepi27](https://github.com/Emmepi27)
