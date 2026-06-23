"""
GeoJSON serialization for flight tracks (illustrative).

RSFly's API is GeoJSON-first so the map frontend (MapLibre GL / deck.gl) can consume
spatial data directly. In production this is done with Django REST Framework +
rest_framework_gis (GeoFeatureModelSerializer); below is a dependency-free version
that turns parsed track points into a GeoJSON Feature.

Note: this serializes the *raw* track. Public RSFly endpoints serve only
masked/aggregated geometry — see ARCHITECTURE.md, "Privacy posture".
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .igc_parser import TrackPoint


def track_to_geojson(
    points: Iterable[TrackPoint],
    properties: dict[str, Any] | None = None,
    altitude: str = "gps",
) -> dict[str, Any]:
    """Build a GeoJSON Feature from ordered track points.

    Coordinates use the GeoJSON order [longitude, latitude, altitude]. ``altitude``
    selects which altitude goes into the Z coordinate: ``"gps"`` or ``"pressure"``.
    """
    pts = list(points)
    if altitude == "pressure":
        coordinates = [[p.lon, p.lat, p.pressure_alt] for p in pts]
    else:
        coordinates = [[p.lon, p.lat, p.gps_alt] for p in pts]

    # A GeoJSON LineString needs >= 2 positions (RFC 7946, section 3.1.4). Degrade
    # gracefully instead of emitting an invalid geometry.
    if len(coordinates) >= 2:
        geometry: dict[str, Any] | None = {"type": "LineString", "coordinates": coordinates}
    elif coordinates:
        geometry = {"type": "Point", "coordinates": coordinates[0]}
    else:
        geometry = None

    return {"type": "Feature", "geometry": geometry, "properties": properties or {}}


def tracks_to_feature_collection(
    tracks: dict[str, Iterable[TrackPoint]],
) -> dict[str, Any]:
    """Wrap several named tracks into a GeoJSON FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": [
            track_to_geojson(points, {"name": name}) for name, points in tracks.items()
        ],
    }


# Production pattern, for reference:
#
#   from rest_framework_gis.serializers import GeoFeatureModelSerializer
#
#   class FlightTrackSerializer(GeoFeatureModelSerializer):
#       class Meta:
#           model = Flight
#           geo_field = "track"        # a PointField / LineStringField
#           fields = ("id", "track", "duration", "max_altitude")
#
# GeoFeatureModelSerializer emits a GeoJSON Feature automatically: it maps the
# geo_field to "geometry" and the remaining fields to "properties".
