"""
Offline and online data analysis and visualization tool for azimuthal
integration of different data acquired with various detectors at
European XFEL.

Base PlotWidget and various concrete PlotWidgets.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
import numpy as np

from .. import pyqtgraph as pg
from ..pyqtgraph import (
    GraphicsView, intColor, mkPen, PlotItem, QtCore, QtGui,
)
from ..misc_widgets import make_brush, make_pen
from ...logger import logger
from ...config import config


class PlotWidget(GraphicsView):
    """GraphicsView widget displaying a single PlotItem.

    Note: it is different from the PlotWidget in pyqtgraph.

    This base class should be used to display plots except image in
    karaboFAI. For image, please refer to ImageView class.
    """
    class BarGraphItem(pg.BarGraphItem):
        def setData(self, x, height):
            """PlotItem interface."""
            self.setOpts(x=x, height=height)

    class ErrorBarItem(pg.ErrorBarItem):
        def setData(self, x, y, **opts):
            """PlotItem interface.

            It should be able to set an empty data set by using
            setData([], []).
            """
            # Expansive code in Python
            keys = ['height', 'width', 'top', 'bottom', 'left', 'right']
            for key in keys:
                opts.setdefault(key)
                if isinstance(opts[key], list):
                    opts[key] = np.array(opts[key])

            if isinstance(x, list):
                x = np.array(x)
            if isinstance(y, list):
                y = np.array(y)
            opts['x'] = x
            opts['y'] = y

            self.opts.update(opts)
            self.path = None
            self.update()
            self.prepareGeometryChange()
            self.informViewBoundsChanged()

    # signals wrapped from PlotItem / ViewBox
    sigRangeChanged = QtCore.Signal(object, object)
    sigTransformChanged = QtCore.Signal(object)

    _pen = mkPen(None)
    _brush_size = 12

    def __init__(self, parent=None, background='default', **kargs):
        """Initialization."""
        super().__init__(parent, background=background)
        if parent is not None:
            parent.registerPlotWidget(self)

        self._data = None  # keep the last data (could be invalid)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)
        self.enableMouse(False)
        self.plotItem = PlotItem(**kargs)
        self.setCentralItem(self.plotItem)

        self.plotItem.sigRangeChanged.connect(self.viewRangeChanged)

    def clear(self):
        """Remove all the items in the PlotItem object."""
        plot_item = self.plotItem
        for i in plot_item.items[:]:
            plot_item.removeItem(i)

    def reset(self):
        """Clear the data of all the items in the PlotItem object."""
        for item in self.plotItem.items:
            item.setData([], [])

    def update(self, data):
        raise NotImplemented

    def close(self):
        self.plotItem.close()
        self.plotItem = None
        self.setParent(None)
        super().close()

    def addItem(self, *args, **kwargs):
        """Explicitly call PlotItem.addItem.

        This method must be here to override the addItem method in
        GraphicsView. Otherwise, people may misuse the addItem method.
        """
        self.plotItem.addItem(*args, **kwargs)

    def removeItem(self, *args, **kwargs):
        self.plotItem.removeItem(*args, **kwargs)

    def plotCurve(self, *args, **kwargs):
        """Add and return a new curve plot."""
        item = pg.PlotCurveItem(*args, **kwargs)
        self.plotItem.addItem(item)
        return item

    def plotScatter(self, *args, **kwargs):
        """Add and return a new scatter plot."""
        item = pg.ScatterPlotItem(*args,
                                  pen=self._pen,
                                  size=self._brush_size, **kwargs)
        self.plotItem.addItem(item)
        return item

    def plotBar(self, x=None, height=None, width=1.0, **kwargs):
        """Add and return a new bar plot."""
        if x is None:
            x = []
            height = []
        item = self.BarGraphItem(x=x, height=height, width=width, **kwargs)
        self.plotItem.addItem(item)
        return item

    def plotErrorBar(self, x=None, y=None, top=None, bottom=None, beam=0.5):
        if x is None:
            x = []
            y = []
        item = self.ErrorBarItem(x=x, y=y, top=top, bottom=bottom, beam=beam)
        self.plotItem.addItem(item)
        return item

    def plotImage(self, *args, **kargs):
        """Add and return a image item."""
        # TODO: this will be done when another branch is merged
        raise NotImplemented

    def setAspectLocked(self, *args, **kwargs):
        self.plotItem.setAspectLocked(*args, **kwargs)

    def setLabel(self, *args, **kwargs):
        self.plotItem.setLabel(*args, **kwargs)

    def setTitle(self, *args, **kwargs):
        self.plotItem.setTitle(*args, **kwargs)

    def addLegend(self, *args, **kwargs):
        self.plotItem.addLegend(*args, **kwargs)

    def hideAxis(self):
        for v in ["left", 'bottom']:
            self.plotItem.hideAxis(v)

    def showAxis(self):
        for v in ["left", 'bottom']:
            self.plotItem.showAxis(v)

    def viewRangeChanged(self, view, range):
        self.sigRangeChanged.emit(self, range)

    def saveState(self):
        return self.plotItem.saveState()

    def restoreState(self, state):
        return self.plotItem.restoreState(state)

    def closeEvent(self, QCloseEvent):
        parent = self.parent()
        if parent is not None:
            parent.unregisterPlotWidget(self)
        super().closeEvent(QCloseEvent)


class SinglePulseAiWidget(PlotWidget):
    """SinglePulseAiWidget class.

    A widget which allows user to visualize the the azimuthal integration
    result of a single pulse. The azimuthal integration result is also
    compared with the average azimuthal integration of all the pulses.
    """
    def __init__(self, *, pulse_id=0, plot_mean=True, parent=None):
        """Initialization.

        :param int pulse_id: ID of the pulse to be plotted.
        :param bool plot_mean: whether to plot the mean AI of all pulses
            if the data is pulse resolved.
        """
        super().__init__(parent=parent)

        self.pulse_id = pulse_id

        self.setLabel('left', "Scattering signal (arb. u.)")
        self.setLabel('bottom', "Momentum transfer (1/A)")

        if plot_mean:
            self.addLegend(offset=(-40, 20))

        self._pulse_plot = self.plotCurve(name="pulse_plot", pen=make_pen("y"))

        if plot_mean:
            self._mean_plot = self.plotCurve(name="mean", pen=make_pen("c"))
        else:
            self._mean_plot = None

    def update(self, data):
        """Override."""
        momentum = data.momentum
        intensities = data.intensities

        if intensities is None:
            return

        if intensities.ndim == 2:
            # pulse resolved data
            max_id = data.n_pulses - 1
            if self.pulse_id <= max_id:
                self._pulse_plot.setData(momentum,
                                         intensities[self.pulse_id])
            else:
                logger.error("<VIP pulse ID>: VIP pulse ID ({}) > Maximum "
                             "pulse ID ({})".format(self.pulse_id, max_id))
                return
        else:
            self._pulse_plot.setData(momentum, intensities)

        if self._mean_plot is not None:
            self._mean_plot.setData(momentum, data.intensity_mean)


class MultiPulseAiWidget(PlotWidget):
    """MultiPulseAiWidget class.

    Widget for displaying azimuthal integration result for all
    the pulses in a train.
    """
    def __init__(self, *, parent=None):
        """Initialization."""
        super().__init__(parent=parent)

        self._n_pulses = 0

        self.setLabel('bottom', "Momentum transfer (1/A)")
        self.setLabel('left', "Scattering signal (arb. u.)")
        self.setTitle(' ')

    def update(self, data):
        """Override."""
        momentum = data.momentum
        intensities = data.intensities

        if intensities is None:
            return

        n_pulses = len(intensities)
        if n_pulses != self._n_pulses:
            self._n_pulses = n_pulses
            # re-plot if number of pulses change
            self.clear()
            for i, intensity in enumerate(intensities):
                self.plotCurve(momentum, intensity,
                               pen=make_pen(i, hues=9, values=5))
        else:
            for item, intensity in zip(self.plotItem.items, intensities):
                item.setData(momentum, intensity)


class SampleDegradationWidget(PlotWidget):
    """SampleDegradationWindow class.

    A widget which allows users to monitor the degradation of the sample
    within a train.
    """
    def __init__(self, *, parent=None):
        """Initialization."""
        super().__init__(parent=parent)

        self._plot = self.plotBar(width=0.6, brush='b')
        self.addItem(self._plot)

        self.setLabel('left', "Integrated difference (arb.)")
        self.setLabel('bottom', "Pulse ID")
        self.setTitle('FOM with respect to the first pulse')

    def update(self, data):
        """Override."""
        foms = data.sample_degradation_foms
        if foms is None:
            return

        self._plot.setData(range(len(foms)), foms)


class RoiValueMonitor(PlotWidget):
    """RoiValueMonitor class.

    Widget for displaying the evolution of the value (integration, median,
    mean) of ROIs.
    """
    def __init__(self, *, window=600, parent=None):
        """Initialization.

        :param int window: window size, i.e. maximum number of trains to
            display. Default = 600.
        """
        super().__init__(parent=parent)

        self._window = window

        self.setLabel('bottom', "Train ID")
        self.setLabel('left', "Intensity (arb. u.)")
        self.setTitle(' ')
        self.addLegend(offset=(-40, 20))

        self._roi1_plot = self.plotCurve(
            name="ROI 1", pen=make_pen(config["ROI_COLORS"][0]))
        self._roi2_plot = self.plotCurve(
            name="ROI 2", pen=make_pen(config["ROI_COLORS"][1]))

    def update(self, data):
        """Override."""
        tids1, roi1_hist, _ = data.roi.roi1_hist
        self._roi1_plot.setData(
            tids1[-self._window:], roi1_hist[-self._window:])
        tids2, roi2_hist, _ = data.roi.roi2_hist
        self._roi2_plot.setData(
            tids2[-self._window:], roi2_hist[-self._window:])

    @QtCore.pyqtSlot(int)
    def onDisplayRangeChange(self, v):
        self._window = v


class CorrelationWidget(PlotWidget):
    """CorrelationWidget class.

    Widget for displaying correlations between FOM and different parameters.
    """
    _colors = ['g', 'c', 'y', 'p']
    _brushes = {
        0: make_brush(_colors[0], 120),
        1: make_brush(_colors[1], 120),
        2: make_brush(_colors[2], 120),
        3: make_brush(_colors[3], 120)
    }
    _opaque_brushes = {
        0: make_brush(_colors[0]),
        1: make_brush(_colors[1]),
        2: make_brush(_colors[2]),
        3: make_brush(_colors[3])
    }

    def __init__(self, idx, *, parent=None):
        """Initialization."""
        super().__init__(parent=parent)

        self._idx = idx

        self.setLabel('left', "FOM (arb. u.)")
        self.setLabel('bottom', "Correlator (arb. u.)")
        self.setTitle(' ')

        self._plot = self.plotScatter(brush=self._brushes[self._idx])
        self._bar = None

    def update(self, data):
        """Override."""
        try:
            correlator, foms, info = getattr(data.correlation,
                                             f'param{self._idx}')
        except AttributeError:
            return

        if isinstance(foms, list):
            self._plot.setData(correlator, foms)
        else:
            self._plot.setData(correlator, foms.avg)
            if self._bar is not None:
                self._bar.setData(x=correlator, y=foms.avg,
                                  top=foms.min, bottom=foms.max)

    def updatePlotType(self, device_id, ppt, resolution):
        self.setLabel('bottom', f"{device_id + ' | ' + ppt} (arb. u.)")

        self.removeItem(self._bar)
        if resolution > 0:
            self._bar = self.plotErrorBar(beam=resolution)
            self._plot.setBrush(self._opaque_brushes[self._idx])
        else:
            self._bar = None
            self._plot.setBrush(self._brushes[self._idx])


class LaserOnOffFomWidget(PlotWidget):
    """LaserOnOffFomWidget class.

    Widget for displaying the evolution of FOM in the Laser On-off analysis.
    """

    def __init__(self, *, parent=None):
        """Initialization."""
        super().__init__(parent=parent)

        self.setLabel('bottom', "Train ID")
        self.setLabel('left', "ROI (arb. u.)")
        self.setTitle(' ')

        self._plot = self.plotScatter(brush=make_brush('c'))

    def update(self, data):
        """Override."""
        tids, foms, _ = data.on_off.foms
        self._plot.setData(tids, foms)


class LaserOnOffAiWidget(PlotWidget):
    """LaserOnOffAiWidget class.

    Widget for displaying the average of the azimuthal integrations
    of laser-on/off pulses.
    """
    def __init__(self, *, parent=None):
        """Initialization."""
        super().__init__(parent=parent)

        self.setLabel('left', "Scattering signal (arb. u.)")
        self.setLabel('bottom', "Momentum transfer (1/A)")
        self.setTitle('Moving average of on- and off- pulses')
        self.addLegend(offset=(-60, 20))

        self._on_pulse = self.plotCurve(name="Laser-on", pen=make_pen("p"))
        self._off_pulse = self.plotCurve(name="Laser-off", pen=make_pen("g"))
        self._diff = self.plotCurve(name="On - Off x 20", pen=make_pen("y"))

    def update(self, data):
        """Override."""
        momentum = data.momentum
        on_pulse = data.on_off.on_pulse
        off_pulse = data.on_off.off_pulse

        if on_pulse is None:
            self._data = None
        else:
            if off_pulse is None:
                if self._data is None:
                    return
                # on-pulse arrives but off-pulse does not
                momentum, on_pulse, off_pulse = self._data
            else:
                self._data = (momentum, on_pulse, off_pulse)

            self._on_pulse.setData(momentum, on_pulse)
            self._off_pulse.setData(momentum, off_pulse)


class LaserOnOffDiffWidget(PlotWidget):
    """LaserOnOffDiffWidget class.

    Widget for displaying the difference of the average of the azimuthal
    integrations of laser-on/off pulses.
    """
    def __init__(self, *, parent=None):
        """Initialization."""
        super().__init__(parent=parent)

        self.setLabel('left', "Scattering signal (arb. u.)")
        self.setLabel('bottom', "Momentum transfer (1/A)")
        self.setTitle('Moving average of on-off')

        self._plot = self.plotCurve(name="On - Off", pen=make_pen("y"))

    def clear(self):
        """Override."""
        self.reset()

    def reset(self):
        """Override."""
        self._plot.setData([], [])

    def update(self, data):
        """Override."""
        momentum = data.momentum
        on_pulse = data.on_off.on_pulse
        off_pulse = data.on_off.off_pulse
        diff = data.on_off.diff

        if on_pulse is None:
            self._data = None
        else:
            if off_pulse is None:
                if self._data is None:
                    return
                # on-pulse arrives but off-pulse does not
                diff = self._data
            else:
                self._data = diff

            self._plot.setData(momentum, diff)
