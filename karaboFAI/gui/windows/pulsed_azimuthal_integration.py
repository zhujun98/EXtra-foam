"""
Offline and online data analysis and visualization tool for azimuthal
integration of different data acquired with various detectors at
European XFEL.

PulsedAzimuthalIntegrationWindow.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
from ..pyqtgraph import QtCore
from ..pyqtgraph.dockarea import Dock

from .base_window import DockerWindow
from ..mediator import Mediator
from ..plot_widgets import (
    MultiPulseAiWidget, PulsedFOMWidget, SinglePulseAiWidget,
    SinglePulseImageView
)


class PulsedAzimuthalIntegrationWindow(DockerWindow):
    """PulsedAzimuthalIntegrationWindow class."""
    title = "pulsed-azimuthal-integration"

    _TOTAL_W = 1500
    _TOTAL_H = 1000

    _LW = 0.5 * _TOTAL_W
    _LH = 0.5 * _TOTAL_H
    _RW = 0.5 * _TOTAL_W
    _RH1 = 0.3 * _TOTAL_H
    _RH2 = 0.4 * _TOTAL_H

    def __init__(self, *args, **kwargs):
        """Initialization."""
        super().__init__(*args, **kwargs)

        if self._pulse_resolved:
            mediator = Mediator()

            self._ai = MultiPulseAiWidget(parent=self)

            self._sample_degradation = PulsedFOMWidget(parent=self)

            self._vip1_ai_dock = None
            self._vip1_img_dock = None
            self._vip1_ai = SinglePulseAiWidget(parent=self)
            self._vip1_img = SinglePulseImageView(parent=self)

            self._vip2_ai_dock = None
            self._vip2_img_dock = None
            self._vip2_ai = SinglePulseAiWidget(parent=self)
            self._vip2_img = SinglePulseImageView(parent=self)

            mediator.vip_pulse_id1_sgn.connect(self.onPulseID1Updated)
            mediator.vip_pulse_id2_sgn.connect(self.onPulseID2Updated)

            self.initUI()

            mediator.updateVipPulseIds()

            self.resize(self._TOTAL_W, self._TOTAL_H)
        else:
            self._ai = SinglePulseAiWidget(parent=self, plot_mean=False)

            self.initUI()
            self.resize(0.6*self._TOTAL_W, 0.6*self._TOTAL_H)

        self.setMinimumSize(900, 600)

        self.update()

    def initUI(self):
        """Override."""
        super().initUI()

    def initPlotUI(self):
        """Override."""

        if self._pulse_resolved:

            # left column

            self._vip1_img_dock = Dock("VIP pulse 0000",
                                       size=(self._LW, self._LH))
            self._docker_area.addDock(self._vip1_img_dock)
            self._vip1_img_dock.addWidget(self._vip1_img)

            self._vip2_img_dock = Dock("VIP pulse 0000",
                                       size=(self._LW, self._LH))
            self._docker_area.addDock(
                self._vip2_img_dock, 'bottom', self._vip1_img_dock)
            self._vip2_img_dock.addWidget(self._vip2_img)

            # right column

            sample_degradation_dock = Dock(
                "Pulse-resolved FOM", size=(self._RW, self._RH1))
            self._docker_area.addDock(sample_degradation_dock, 'right')
            sample_degradation_dock.addWidget(self._sample_degradation)

            ai_dock = Dock("Normalized azimuthal Integration",
                           size=(self._RW, self._RH2))
            self._docker_area.addDock(ai_dock, 'top', sample_degradation_dock)
            ai_dock.addWidget(self._ai)

            self._vip1_ai_dock = Dock("VIP pulse 0000 - AI",
                                      size=(self._RW, self._RH1),
                                      autoOrientation=False)
            self._vip1_ai_dock.setOrientation('vertical')
            self._docker_area.addDock(self._vip1_ai_dock, 'top', ai_dock)
            self._vip1_ai_dock.addWidget(self._vip1_ai)

            self._vip2_ai_dock = Dock("VIP pulse 0000 - AI",
                                      size=(self._RW, self._RH1),
                                      autoOrientation=False)
            self._vip2_ai_dock.setOrientation('vertical')
            self._docker_area.addDock(
                self._vip2_ai_dock, 'right', self._vip1_ai_dock)
            self._vip2_ai_dock.addWidget(self._vip2_ai)

        else:
            ai_dock = Dock("Normalized azimuthal Integration",
                           size=(self._TOTAL_W, self._TOTAL_H))
            self._docker_area.addDock(ai_dock)
            ai_dock.addWidget(self._ai)

    @QtCore.pyqtSlot(int)
    def onPulseID1Updated(self, value):
        self._vip1_ai_dock.setTitle("VIP pulse {:04d} - AI".format(value))
        self._vip1_img_dock.setTitle("VIP pulse {:04d}".format(value))
        self._vip1_ai.pulse_id = value
        self._vip1_img.pulse_id = value

    @QtCore.pyqtSlot(int)
    def onPulseID2Updated(self, value):
        self._vip2_ai_dock.setTitle("VIP pulse {:04d} - AI".format(value))
        self._vip2_img_dock.setTitle("VIP pulse {:04d}".format(value))
        self._vip2_ai.pulse_id = value
        self._vip2_img.pulse_id = value