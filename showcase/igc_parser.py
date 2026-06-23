"""
IGC B-record parser (illustrative).

IGC is the open flight-recorder format used in free flight. Each 'B' record is one
GPS fix. This is an illustrative parser, rewritten for this repo, that turns an
uploaded flight log into an ordered list of 3D track points. It deliberately handles
the real-world details that trip up naive parsers — the date lives in the 'HFDTE'
header (B-records carry only time-of-day), flights can cross midnight UTC, fixes can
be flagged invalid ('V'), and lines can be malformed. No production code or data is
included.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone


@dataclass(frozen=True)
class TrackPoint:
    timestamp: datetime   # UTC; date from the header, so midnight-crossing flights stay ordered
    lat: float            # decimal degrees, +N / -S
    lon: float            # decimal degrees, +E / -W
    pressure_alt: int     # metres (barometric)
    gps_alt: int          # metres (GPS)
    valid: bool           # IGC fix-validity flag: True if 'A' (3D fix), False if 'V'


def _dm_to_decimal(degrees: int, minutes_thousandths: int, hemisphere: str) -> float:
    """Convert IGC 'degrees + (minutes * 1000)' to signed decimal degrees."""
    decimal = degrees + minutes_thousandths / 60000.0  # minutes*1000, so / (1000 * 60)
    return -decimal if hemisphere in ("S", "W") else decimal


def parse_header_date(lines: list[str]) -> date | None:
    """Read the flight date (DDMMYY) from the IGC 'HFDTE' header.

    Handles both the legacy 'HFDTE120625' and the newer 'HFDTEDATE:120625,01'.
    Returns None if no header date is present.
    """
    for line in lines:
        if line.startswith("HFDTE"):
            digits = "".join(ch for ch in line if ch.isdigit())
            if len(digits) >= 6:
                day, month, year = int(digits[0:2]), int(digits[2:4]), int(digits[4:6])
                return date(2000 + year, month, day)
    return None


def _parse_b_fields(line: str):
    """Parse one IGC 'B' record into raw fields, or None for non-B / malformed lines.

    Layout:  B HHMMSS DDMMmmm[N/S] DDDMMmmm[E/W] [A/V] PPPPP GGGGG
    """
    if not line.startswith("B") or len(line) < 35:
        return None
    try:
        fix_time = time(int(line[1:3]), int(line[3:5]), int(line[5:7]))
        lat = _dm_to_decimal(int(line[7:9]), int(line[9:14]), line[14])
        lon = _dm_to_decimal(int(line[15:18]), int(line[18:23]), line[23])
        valid = line[24] == "A"
        pressure_alt = int(line[25:30])
        gps_alt = int(line[30:35])
    except (ValueError, IndexError):
        return None  # malformed B-record: skip this fix, don't abort the whole flight
    return fix_time, lat, lon, pressure_alt, gps_alt, valid


def parse_igc(lines: list[str], flight_date: date | None = None) -> list[TrackPoint]:
    """Parse IGC lines into an ordered list of 3D track points (UTC).

    B-records carry only the time of day, so we take the date from the 'HFDTE'
    header and roll over to the next day whenever the clock goes backwards — this
    keeps flights that cross midnight UTC monotonically ordered.
    """
    flight_date = flight_date or parse_header_date(lines) or date(1970, 1, 1)
    points: list[TrackPoint] = []
    prev_time: time | None = None
    day_offset = 0

    for line in lines:
        fields = _parse_b_fields(line.strip())
        if fields is None:
            continue
        fix_time, lat, lon, pressure_alt, gps_alt, valid = fields
        if prev_time is not None and fix_time < prev_time:
            day_offset += 1  # crossed midnight UTC
        prev_time = fix_time
        timestamp = datetime.combine(flight_date, fix_time, tzinfo=timezone.utc) + timedelta(
            days=day_offset
        )
        points.append(TrackPoint(timestamp, lat, lon, pressure_alt, gps_alt, valid))

    return points
