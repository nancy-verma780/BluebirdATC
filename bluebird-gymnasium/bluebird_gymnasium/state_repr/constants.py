import numpy as np

SCALER_LAT = np.pi / 2
SCALER_LON = np.pi
SCALER_BEARING = 2 * np.pi

SCALER_DIST = 50  # nautical miles
SCALER_DIST_DIFF = 20  # nautical miles
SCALER_CENTRELINE_DIST = 50  # nautical miles
SCALER_EXIT_DIST = 50  # nautical miles
SCALER_INCOMM_DIST = 10
SCALER_OUTCOMM_DIST = 10
SCALER_AC_OTHER_DIST = 50
SCALER_AC_NF_DIST = 50
SCALER_AC_NB_DIST = 10
SCALER_FL = 160  # TODO: need to be updated to 333 if CLIP_FL is not updated
SCALER_FL_DIFF = 20
SCALER_SPEED = 200  # nautical miles per hour (knots)
SCALER_SPEED_DIFF = 30  # nautical miles per hour (knots)
SCALER_VERTICAL_SPEED = 1000  # feet per minute

CLIP_DIST = 150  # nautical miles
CLIP_DIST_DIFF = 60  # nautical miles
CLIP_INCOMM_DIST = 30  # nautical miles
CLIP_OUTCOMM_DIST = 30  # nautical miles
CLIP_AC_NB_DIST = 30  # nautical miles
CLIP_FL = 1000  # flight level # TODO: might need to be updated to 480?
CLIP_FL_DIFF = 60
CLIP_SPEED = 600  # nautical miles per hour (knots)
CLIP_SPEED_DIFF = 90  # nautical miles per hour (knots)
CLIP_VERTICAL_SPEED = 3000  # feet per minute
