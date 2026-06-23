from datetime import date, timezone

from showcase.igc_parser import parse_header_date, parse_igc

HFDTE = "HFDTEDATE:120625,01"  # 12 June 2025


def b(time_s, lat="5206343N", lon="00006198W", valid="A", palt="00587", galt="00558"):
    """Build a synthetic IGC B-record."""
    return f"B{time_s}{lat}{lon}{valid}{palt}{galt}"


def test_parses_basic_fix():
    points = parse_igc([HFDTE, b("110135")])
    assert len(points) == 1
    p = points[0]
    assert abs(p.lat - 52.10572) < 1e-4
    assert abs(p.lon - (-0.1033)) < 1e-4
    assert p.pressure_alt == 587
    assert p.gps_alt == 558
    assert p.valid is True
    assert p.timestamp.tzinfo == timezone.utc
    assert p.timestamp.date() == date(2025, 6, 12)


def test_midnight_rollover_keeps_order():
    points = parse_igc([HFDTE, b("235959"), b("000001")])
    assert points[1].timestamp > points[0].timestamp
    assert points[1].timestamp.date() == date(2025, 6, 13)


def test_invalid_fix_flag_preserved():
    points = parse_igc([HFDTE, b("110135", valid="V")])
    assert points[0].valid is False


def test_negative_pressure_altitude():
    points = parse_igc([HFDTE, b("110135", palt="-0012")])
    assert points[0].pressure_alt == -12


def test_malformed_b_record_is_skipped_not_fatal():
    points = parse_igc([HFDTE, "B" + "X" * 40, b("110135"), "Bshort"])
    assert len(points) == 1  # only the good fix survives


def test_non_b_lines_ignored():
    points = parse_igc([HFDTE, "HFPLTPILOT:Manuel", "LCOMMENT line", b("110135")])
    assert len(points) == 1


def test_header_date_legacy_and_modern():
    assert parse_header_date(["HFDTE120625"]) == date(2025, 6, 12)
    assert parse_header_date(["HFDTEDATE:120625,01"]) == date(2025, 6, 12)
    assert parse_header_date(["B1101355206343N00006198WA0058700558"]) is None
