from __future__ import annotations

from math import floor

from typing_extensions import override

from bluebird_dt.core import Aircraft, Fixes, Pos4D, WindField
from bluebird_dt.predictor.predictor import Predictor


class RouteFollowPredictor(Predictor):
    """
    Evolves the Aircraft with constant speed and infinite acceleration along its Route.
    """

    def __init__(self, dt: float, fix_proximity_threshold: float, fixes: Fixes | None):
        """
        Construct a new instance.

        Parameters
        ----------
        dt: float
            The internal step time of the predictor. The time taken between each control point within the returned
            Trajectory is dt.
        fix_proximity_threshold: float
            When an Aircraft is <= fix_proximity_threshold distance from the next Fix on its Route, the Fix is
            considered to have been passed. The next target Fix on Route for the Aircraft is then updated.
        fixes: Fixes | None
            Fixes from the airspace that aircraft are flying in
        """

        super().__init__(dt, fix_proximity_threshold, fixes)

    @override
    def _predict(
        self,
        aircraft: Aircraft,
        time_evolve: float,
        environment_time: float = 0.0,
        wind_field: WindField | None = None,  # noqa: ARG002
    ) -> tuple[list[Pos4D], Aircraft]:
        """
        Calculate the trajectory of an aircraft over time_evolve time and evolve the aircraft to the last point in
        the trajectory.

        This is used in two different ways:
        (1) to evolve the aircraft by moving it to the last point in the predicted trajectory.
            In this case time_evolve is normally the radar period.
        (2) to predict a longer trajectory for use by agents, conflict detection etc.
            In this case time_evolve is normally several minutes.

        Parameters
        ----------
        aircraft: Aircraft
            The aircraft to calculate a trajectory for
        time_evolve: float
            The duration [sec] for which to calculate the trajectory and evolve the aircraft
        environment_time: float, optional
            Current time in the environment in seconds (Posix/UNIX)
        wind_field: WindField | None, optional
            The current wind field - not used in this predictor

        Returns
        -------
        Trajectory
            The predicted trajectory
        Aircraft
            The aircraft evolved to the last point in the predicted trajectory
        """

        # Evolve Aircraft
        control_points: list[Pos4D] = []
        time = 0.0
        default_aircraft_speed = 300.0

        # Create an array of step sizes to use for this trajectory.
        # Normally time_evolve is a multiple of dt, so the step sizes are dt, but this may not be the case if
        # the aircraft has just been added. In this case, take a smaller step first, so the remaining steps are dt.
        steps = [time_evolve % self.dt] + [self.dt] * floor(time_evolve / self.dt)

        for step in [s for s in steps if s > 0.0]:
            pos = aircraft.pos2d()

            # If still route following - set aircraft's heading pointing towards next fix
            if aircraft.on_route:
                target_pos = self.get_target_pos(aircraft)
                aircraft.heading = pos.bearing_to(target_pos)

            if aircraft.speed_tas is None:
                aircraft.speed_tas = default_aircraft_speed

            dx = aircraft.speed_tas * (step / 3600.0)
            new_pos = pos.forward(dx, aircraft.heading)

            aircraft.lat = new_pos.lat
            aircraft.lon = new_pos.lon

            # If still route following - update next_fix_index. If past the last fix,
            # set the aircraft to be not route following.
            if aircraft.on_route and new_pos.distance(target_pos) <= self.fix_proximity_threshold:
                aircraft.next_fix_index += 1
                if aircraft.next_fix_index >= len(aircraft.flight_plan.route.current):
                    aircraft.next_fix_index = None
                    aircraft.on_route = False

            time += step

            cp = Pos4D(
                lat=aircraft.lat,
                lon=aircraft.lon,
                fl=aircraft.fl,
                time=environment_time + time,
            )
            control_points.append(cp)

        return control_points, aircraft
