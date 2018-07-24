from enum import Enum
import os


class DataSource(Enum):
    CALIBRATED = 1  # From file or Karabo-bridge
    ASSEMBLED = 2  # Assembled by hardware
    PROCESSED = 3  # From the Middle-layer device


class Config:
    # distance sample - detector plan (orthogonal distance, not along the
    # beam), in meter
    DIST = 0.2
    # coordinate of the point of normal incidence along the detector's first
    # dimension, in meter
    CENTER_Y = 620
    # coordinate of the point of normal incidence along the detector's second
    # dimension, in meter
    CENTER_X = 580
    PIXEL_SIZE = 0.5e-3  # in meter

    ENERGY = 9.30  # in, keV
    LAMBDA_R = 12.3984 / ENERGY * 1e-10  # in m

    PULSES_PER_TRAIN = 16

    INTEGRATION_METHOD = "BBox"
    RADIAL_RANGE = (0.2, 5)  # the lower and upper range of the radial unit
    N_POINTS = 512  # number of points in the output pattern
    MASK_RANGE = (0, 1e4)  # image pixels beyond this range will be masked

    # The following is valid-ish for the 20180318 geometry
    QUAD_POSITIONS = [(-11.4, -229), (11.5, -8), (-254.5, 16), (-278.5, -275)]

    DEFAULT_GEOMETRY_FILE = os.path.join(os.path.expanduser("~"),
                                         "fxe-data/lpd_mar_18.h5")

    # *********************************************************************
    MAX_QUEUE_SIZE = 10

    # *********************************************************************
    UPDATE_FREQUENCY = 10  # in Hz

    WINDOW_HEIGHT = 800
    WINDOW_WIDTH = 640
    MAX_WINDOW_HEIGHT = 1000

    MAX_LOGGING = 1000
    LOGGER_FONT_SIZE = 12

    LINE_PLOT_WIDTH = WINDOW_WIDTH - 20
    LINE_PLOT_HEIGHT = 250
    LINE_PLOT_LEGEND_OFFSET = (-10, -50)

    # *********************************************************************
    X_LABEL = "Momentum"
    Y_LABEL = "Intensity"

    CUSTOM_PEN = [
        {'color': (255, 0, 255), 'width': 3},
        {'color': (0, 255, 0), 'width': 3},
        {'color': (255, 255, 0), 'width': 3}
    ]