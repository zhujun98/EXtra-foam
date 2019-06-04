"""
Offline and online data analysis and visualization tool for azimuthal
integration of different data acquired with various detectors at
European XFEL.

Helper functions.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
import psutil
import multiprocessing as mp
import functools
import time

from .logger import logger


# profiler will only print out information if the execution of the given
# function takes more than the threshold value.
PROFILER_THREASHOLD = 10.0  # in ms


def profiler(info):
    def wrap(f):
        @functools.wraps(f)
        def timed_f(*args, **kwargs):
            t0 = time.process_time()
            result = f(*args, **kwargs)
            dt_ms = 1000 * (time.process_time() - t0)
            if dt_ms > PROFILER_THREASHOLD:
                logger.debug(f"Process time spent on {info}: {dt_ms:.3f} ms")
            return result
        return timed_f
    return wrap


def get_system_memory():
    """Get the total system memory."""
    return psutil.virtual_memory().total


def check_system_resource():
    """Check the resource of the current system"""
    n_cpus = mp.cpu_count()

    n_gpus = 0

    total_memory = get_system_memory()

    return n_cpus, n_gpus, total_memory


class _MetaSingleton(type):
    """Meta class and bookkeeper for Singletons."""
    _instances = dict()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
