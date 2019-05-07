"""
Offline and online data analysis and visualization tool for azimuthal
integration of different data acquired with various detectors at
European XFEL.

RoiProcessor.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
import copy

import numpy as np

from .base_processor import (
    CompositeProcessor, LeafProcessor, SharedProperty,
    StopCompositionProcessing
)
from ..exceptions import ProcessingError
from ...algorithms import intersection, normalize_curve
from ...config import config, RoiFom, PumpProbeType
from ...helpers import profiler


class RoiProcessor(CompositeProcessor):
    """RoiProcessor class.

    Process region of interest.

    Attributes:
        _rois (list): a list of ROI regions (w, h, x, y) or None if the
            corresponding ROI is not activated.
        fom_type (RoiFom): type of ROI FOM.
    """
    _raw_rois = SharedProperty()
    _roi_fom_handler = SharedProperty()

    def __init__(self):
        super().__init__()

        # initialization
        self._raw_rois = [None] * len(config["ROI_COLORS"])

        self._fom_type = None
        self._roi_fom_handler = None

        self.add(RoiFomProcessor())
        self.add(RoiPumpProbeRoiProcessor())

    @property
    def fom_type(self):
        return self._fom_type

    @fom_type.setter
    def fom_type(self, v):
        self._fom_type = v

        if v == RoiFom.SUM:
            self._roi_fom_handler = np.sum
        elif v == RoiFom.MEAN:
            self._roi_fom_handler = np.mean
        else:
            self._roi_fom_handler = None
            self._fom_type = None

    def set_roi(self, rank, value):
        """Set ROI.

        :param int rank: ROI rank (index).
        :param tuple value: (w, h, x, y) of the ROI. None for unset.
        """
        self._raw_rois[rank-1] = value

    @staticmethod
    def get_roi_image(roi_region, img, copy=True):
        w, h, x, y = roi_region
        return np.array(img[y:y + h, x:x + w], copy=copy)


class RoiFomProcessor(LeafProcessor):
    """RoiFomProcessor class.

    Take the on and off images calculated by the PumpProbeProcessor
    and extract the ROIs of both on and off images using ROI1. The
    figure-of-merit is sum or mean of the difference between these
    two ROI images.
    """
    @profiler("ROI processor")
    def process(self, processed, raw=None):
        """Override.

        Note: We need to put some data in the history, even if ROI is not
        activated. This is required for the case that different ROIs are
        activated at different times.
        """
        if self._roi_fom_handler is None:
            return

        tid = processed.tid
        if tid > 0:
            img = processed.image.masked_mean

            rois = copy.copy(self._raw_rois)
            for i, roi in enumerate(rois):
                # it should be valid to set ROI intensity to zero if the data
                # is not available
                fom = 0
                if roi is not None:
                    roi = intersection(*roi, *img.shape[::-1], 0, 0)
                    # if w > 0 and h > 0
                    if roi[0] > 0 and roi[1] > 0:
                        # set the corrected roi
                        setattr(processed.roi, f"roi{i+1}", roi)

                        roi_img = RoiProcessor.get_roi_image(
                            roi, img, copy=False)

                        proj_x = np.sum(roi_img, axis=-2)
                        proj_y = np.sum(roi_img, axis=-1)
                        setattr(processed.roi, f"roi{i + 1}_proj_x", proj_x)
                        setattr(processed.roi, f"roi{i + 1}_proj_y", proj_y)

                        fom = self._roi_fom_handler(roi_img)

                setattr(processed.roi, f"roi{i+1}_hist", (tid, fom))


class RoiPumpProbeRoiProcessor(CompositeProcessor):
    """RoiPumpProbeRoiProcessor class.

    Extract the ROI image for on/off pulses respectively.
    """
    def __init__(self):
        super().__init__()

        self.add(RoiPumpProbeProj1dProcessor())

    @profiler("ROI processor")
    def process(self, processed, raw=None):
        # use ROI1 for signal
        roi = processed.roi.roi1
        if roi is None:
            raise StopCompositionProcessing

        # use ROI2 for background
        roi_bkg = processed.roi.roi2
        if roi_bkg is not None and roi_bkg[:2] != roi[:2]:
            raise ProcessingError("Shapes of ROI1 and ROI2 are different")

        on_image = processed.pp.on_image_mean
        off_image = processed.pp.off_image_mean
        if on_image is None or off_image is None:
            return StopCompositionProcessing

        on_roi = RoiProcessor.get_roi_image(roi, on_image)
        off_roi = RoiProcessor.get_roi_image(roi, off_image)
        # ROI background subtraction, which is also a kind of normalization
        if roi_bkg is not None:
            on_roi_bkg = RoiProcessor.get_roi_image(
                roi_bkg, on_image, copy=False)
            off_roi_bkg = RoiProcessor.get_roi_image(
                roi_bkg, off_image, copy=False)
            on_roi -= on_roi_bkg
            off_roi -= off_roi_bkg

        # set the current on/off ROIs
        processed.pp.on_roi = on_roi
        processed.pp.off_roi = off_roi

        if processed.pp.analysis_type == PumpProbeType.ROI:
            processed.pp.data = (None, on_roi, off_roi)
            _, on_ma, off_ma = processed.pp.data  # get the moving average

            # for now, no normalization is applied
            norm_on_ma = np.copy(on_ma)
            norm_off_ma = np.copy(off_ma)
            norm_on_off_ma = norm_on_ma - norm_off_ma

            if processed.pp.abs_difference:
                fom = self._roi_fom_handler(np.abs(norm_on_off_ma))
            else:
                fom = self._roi_fom_handler(norm_on_off_ma)

            processed.pp.norm_on_ma = norm_on_ma
            processed.pp.norm_off_ma = norm_off_ma
            processed.pp.norm_on_off_ma = norm_on_off_ma
            processed.pp.fom = (processed.tid, fom)


class RoiPumpProbeProj1dProcessor(LeafProcessor):
    """RoiPumpProbeProj1dProcessor class.

    Calculate the 1D projection for on/off ROIs.
    """
    def __init__(self):
        super().__init__()

    def process(self, processed, raw=None):
        if processed.pp.analysis_type == PumpProbeType.ROI_PROJECTION_X:
            axis = -2
        elif processed.pp.analysis_type == PumpProbeType.ROI_PROJECTION_Y:
            axis = -1
        else:
            return

        on_roi = processed.pp.on_roi
        off_roi = processed.pp.off_roi

        x_data = np.arange(on_roi.shape[::-1][axis])
        # 1D projection
        on_data = np.sum(on_roi, axis=axis)
        off_data = np.sum(off_roi, axis=axis)

        # set data and calculate moving average
        processed.pp.data = (x_data, on_data, off_data)
        _, on_ma, off_ma = processed.pp.data

        norm_on_ma = normalize_curve(on_ma, x_data, x_data[0], x_data[-1])
        norm_off_ma = normalize_curve(off_ma, x_data, x_data[0], x_data[-1])
        norm_on_off_ma = norm_on_ma - norm_off_ma
        if processed.pp.abs_difference:
            fom = np.sum(np.abs(norm_on_off_ma))
        else:
            fom = np.sum(norm_on_off_ma)

        processed.pp.norm_on_ma = norm_on_ma
        processed.pp.norm_off_ma = norm_off_ma
        processed.pp.norm_on_off_ma = norm_on_off_ma
        processed.pp.fom = (processed.tid, fom)