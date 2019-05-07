"""
Offline and online data analysis and visualization tool for azimuthal
integration of different data acquired with various detectors at
European XFEL.

Miscellaneous algorithms.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
import numpy as np

from .sampling import slice_curve


def normalize_curve(y, x, x_min=None, x_max=None):
    """Normalize y by the integration of y within a given range of x.

    :param numpy.ndarray y: 1D array.
    :param numpy.ndarray x: 1D array.
    :param None/float x_min: minimum x value.
    :param None/float x_max: maximum x value.

    :return numpy.ndarray: the normalized y.

    :raise ValueError
    """
    # if y contains only 0
    if not np.count_nonzero(y):
        return np.copy(y)

    # get the integration
    itgt = np.trapz(*slice_curve(y, x, x_min, x_max))

    if itgt == 0:
        raise ValueError("Normalized by 0!")

    return y / itgt