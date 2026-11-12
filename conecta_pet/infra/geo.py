import math
from typing import Optional

EARTH_RADIUS_KM = 6371.0


def calculate_distance_km(
    lat1: Optional[float],
    lng1: Optional[float],
    lat2: Optional[float],
    lng2: Optional[float],
) -> Optional[float]:
    """
    Calcula a distância geodésica (Haversine) em quilômetros entre duas coordenadas (lat, lng).
    """
    if lat1 is None or lng1 is None or lat2 is None or lng2 is None:
        return None

    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(EARTH_RADIUS_KM * c, 1)


def get_geo_cell_key(lat: Optional[float], lng: Optional[float], precision: int = 2) -> str:
    """
    Agrupa coordenadas em uma célula geográfica (~1.1 km na precisão 2)
    para maximizar a taxa de Cache Hit regional (estilo iFood/Uber H3).
    """
    if lat is None or lng is None or math.isnan(lat) or math.isnan(lng):
        return "global"
    return f"{lat:.{precision}f}:{lng:.{precision}f}"
