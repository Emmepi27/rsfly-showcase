"""
Spatial proximity with GeoDjango + PostGIS (illustrative).

A common RSFly task: "which known launch sites are within N metres of this point?".
The classic PostGIS gotcha is that distances on geometry in SRID 4326 are measured in
*degrees*, not metres. Using the ``geography`` type (or a geodetic distance) makes
``ST_DWithin`` work in metres. This is a standard pattern — not RSFly-specific tuning —
and requires Django + PostGIS to run.
"""
from __future__ import annotations

# Illustrative model (not included as a runnable app):
#
#   from django.contrib.gis.db import models
#
#   class LaunchSite(models.Model):
#       name = models.CharField(max_length=120)
#       # geography=True -> ST_DWithin / Distance return metres, not degrees
#       location = models.PointField(srid=4326, geography=True)
#
#       class Meta:
#           indexes = [models.Index(fields=["location"])]  # GiST index on the geometry


def launch_sites_within(longitude: float, latitude: float, radius_m: float):
    """Return launch sites within ``radius_m`` metres of (lon, lat), nearest first.

    The filtering and distance computation run in PostGIS, not in Python: ``__dwithin``
    uses the GiST index, and ``Distance`` returns metres because the column is a
    ``geography``.
    """
    from django.contrib.gis.db.models.functions import Distance
    from django.contrib.gis.geos import Point
    from django.contrib.gis.measure import D

    from .models import LaunchSite  # illustrative; no such module in this repo

    point = Point(longitude, latitude, srid=4326)
    return (
        LaunchSite.objects.filter(location__dwithin=(point, D(m=radius_m)))
        .annotate(distance=Distance("location", point))
        .order_by("distance")
    )
