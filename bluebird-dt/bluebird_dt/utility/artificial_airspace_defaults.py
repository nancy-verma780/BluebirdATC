from typing import TypedDict


class AirspaceSettingsType(TypedDict):
    penumbra_fl: int
    penumbra_lat: int
    x_sector_pairs: list[tuple[str, str]]


AIRSPACE_SETTINGS = AirspaceSettingsType(
    penumbra_fl=10,
    penumbra_lat=20,
    # pairs of boundary then outer fixes for the x-sector - required for lateral offset calculations
    x_sector_pairs=[
        ("GATES", "SIN"),
        ("DEMON", "SANTA"),
        ("WITCH", "SIREN"),
        ("HAUNT", "LIMBO"),
    ],
)
