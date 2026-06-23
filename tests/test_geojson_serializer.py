from showcase.geojson_serializer import track_to_geojson, tracks_to_feature_collection
from showcase.igc_parser import parse_igc

HFDTE = "HFDTEDATE:120625,01"


def b(time_s):
    return f"B{time_s}5206343N00006198WA0058700558"


def test_linestring_feature():
    points = parse_igc([HFDTE, b("110135"), b("110145")])
    feature = track_to_geojson(points, {"name": "demo"})
    assert feature["type"] == "Feature"
    assert feature["geometry"]["type"] == "LineString"
    assert len(feature["geometry"]["coordinates"]) == 2
    lon, lat, alt = feature["geometry"]["coordinates"][0]
    assert abs(lon - (-0.1033)) < 1e-4
    assert abs(lat - 52.10572) < 1e-4
    assert alt == 558
    assert feature["properties"]["name"] == "demo"


def test_single_point_is_not_an_invalid_linestring():
    points = parse_igc([HFDTE, b("110135")])
    feature = track_to_geojson(points)
    assert feature["geometry"]["type"] == "Point"


def test_empty_track_has_null_geometry():
    feature = track_to_geojson([])
    assert feature["geometry"] is None


def test_pressure_altitude_in_z():
    points = parse_igc([HFDTE, b("110135"), b("110145")])
    feature = track_to_geojson(points, altitude="pressure")
    assert feature["geometry"]["coordinates"][0][2] == 587


def test_feature_collection():
    points = parse_igc([HFDTE, b("110135"), b("110145")])
    collection = tracks_to_feature_collection({"a": points, "b": points})
    assert collection["type"] == "FeatureCollection"
    assert len(collection["features"]) == 2
