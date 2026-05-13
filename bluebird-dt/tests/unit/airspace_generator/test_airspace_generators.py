import pytest

from bluebird_dt.airspace_generator import SectorI, SectorX, SectorXPlus, SectorY


@pytest.mark.parametrize(
    "width, height, fl_limits, alpha, origin",
    [
        (-1, 120, (0, 400), 45, (0, 0)),  # Negative width
        (20, -1, (0, 400), 45, (0, 0)),  # Negative height
        (20, 120, (-1, 400), 45, (0, 0)),  # Negative fl_limit[0]
        (20, 120, (0, -1), 45, (0, 0)),  # Negative fl_limit[1]
        (20, 120, (400, 400), 45, (0, 0)),  # fl_limit[0] == fl_limit[1]
        (20, 120, (401, 400), 45, (0, 0)),  # fl_limit[0] < fl_limit[1]
        (20, 120, (0, 400), 45, (-181, 0)),  # Origin longitude < -180
        (20, 120, (0, 400), 45, (181, 0)),  # Origin longitude > 180
        (20, 120, (0, 400), 45, (0, -91)),  # Origin latitude < -90
        (20, 120, (0, 400), 45, (0, 91)),  # Origin latitude > 90
    ],
)
def test_sector_ixy_shared_invalid_values(width, height, fl_limits, alpha, origin):
    """
    Test sectors I, X, and Y return a ValueError when initialised with invalid width,
    height, fl_limits, and/or origin values.
    """

    with pytest.raises(ValueError):
        SectorI(width, height, fl_limits, alpha, origin)
    with pytest.raises(ValueError):
        SectorX(width, height, fl_limits, alpha, origin)
    with pytest.raises(ValueError):
        SectorY(width, height, fl_limits, alpha, origin)


@pytest.mark.parametrize("alpha", [-181, 181])
def test_sector_i_invalid_alpha(alpha):
    """
    Test SectorI returns a ValueError when initialised with an invalid alpha value.
    """

    with pytest.raises(ValueError):
        SectorI(20, 120, (0, 400), alpha)


@pytest.mark.parametrize("alpha", [-1, 91])
def test_sector_x_invalid_alpha(alpha):
    """
    Test SectorX returns a ValueError when initialised with an invalid alpha value.
    """

    with pytest.raises(ValueError):
        SectorX(20, 120, (0, 400), alpha)


@pytest.mark.parametrize("alpha", [-1, 181])
def test_sector_y_invalid_alpha(alpha):
    """
    Test SectorY returns a ValueError when initialised with an invalid alpha value.
    """

    with pytest.raises(ValueError):
        SectorY(20, 120, (0, 400), alpha)


@pytest.mark.parametrize(
    ("sector_kwargs", "expected_num_routes"),
    [
        pytest.param({}, 10, id="default_geometry"),
        pytest.param(
            {
                "rotation_deg": 0.0,
                "southern_leg_rotation_deg": 10.0,
                "L1": 2.5,
                "L2": 4.0,
                "L3": 4.5,
                "L4": 3.0,
                "D": 1.8,
            },
            12,
            id="compact_geometry",
        ),
        pytest.param(
            {
                "origin": (-3.5, 52.0),
                "rotation_deg": 67.5,
                "southern_leg_rotation_deg": 55.0,
                "half_width_nmi": 7.5,
                "L1": 4.5,
                "L2": 5.5,
                "L3": 6.0,
                "L4": 5.0,
                "W": 0.8,
                "D": 2.0,
                "F": 0.75,
            },
            9,
            id="rotated_offset_geometry",
        ),
    ],
)
def test_sector_xplus_generate_airspace_basics(sector_kwargs, expected_num_routes):
    """
    Generate SectorXPlus airspace and verify valid geometry across multiple parameter combinations.
    """
    airspace, routes = SectorXPlus(**sector_kwargs).generate_airspace()

    assert list(airspace.sectors) == ["sector_xplus"]

    sector = airspace.sectors["sector_xplus"]
    assert len(sector.volumes) == 1

    volume = sector.volumes[0]
    assert (volume.min_fl, volume.max_fl) == sector_kwargs.get("fl_limits", (200, 400))

    polygon = volume.area.boundary
    assert polygon.geom_type == "Polygon"
    assert polygon.area > 0
    assert polygon.is_valid
    assert polygon.boundary.is_simple
    assert polygon.exterior.is_ring
    assert polygon.exterior.coords[0] == polygon.exterior.coords[-1]
    assert len(polygon.interiors) == 0

    expected_fixes = {"EGL", "QUAIL", "SWIFT", "GOOSE", "PEL", "CRANE", "HERON", "FINCH", "ROBIN", "ALB", "MACAW"}
    assert airspace.fixes.as_set == expected_fixes

    terminals = {"ROBIN", "HERON", "PEL", "SWIFT"}
    assert len(routes) == expected_num_routes

    for route in routes:
        assert route.filed[0] in terminals
        assert route.filed[-1] in terminals
        assert route.filed[0] != route.filed[-1]
        assert set(route.filed).issubset(expected_fixes)


def test_sector_xplus_route_filtering_by_turn_angle():
    """
    Generate SectorXPlus airspaces with different maximum turn angles and compare number of routes created.
    
    Read the SectorXPlus documentation about what the parameter max_turn_angle_deg does.
    """
    _, routes_default = SectorXPlus(max_turn_angle_deg=90).generate_airspace()
    _, routes_strict = SectorXPlus(max_turn_angle_deg=10).generate_airspace()

    assert len(routes_strict) < len(routes_default)
