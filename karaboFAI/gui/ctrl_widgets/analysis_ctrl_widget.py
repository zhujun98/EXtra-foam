"""
Offline and online data analysis and visualization tool for azimuthal
integration of different data acquired with various detectors at
European XFEL.

AnalysisCtrlWidget.

Author: Jun Zhu <jun.zhu@xfel.eu>, Ebad Kamil <ebad.kamil@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
from ..pyqtgraph import QtCore, QtGui

from .base_ctrl_widgets import AbstractCtrlWidget


class AnalysisCtrlWidget(AbstractCtrlWidget):
    """Widget for setting up the general analysis parameters."""

    _pulse_id_validator = QtGui.QIntValidator(0, 2699)

    def __init__(self, *args, **kwargs):
        super().__init__("General analysis setup", *args, **kwargs)

        # We keep the definitions of attributes which are not used in the
        # PULSE_RESOLVED = True case. It makes sense since these attributes
        # also appear in the defined methods.

        if self._pulse_resolved:
            min_pulse_id = 0
            max_pulse_id = self._pulse_id_validator.top()
            vip_pulse_id1 = 0
            vip_pulse_id2 = 1
        else:
            min_pulse_id = 0
            max_pulse_id = 0
            vip_pulse_id1 = 0
            vip_pulse_id2 = 0

        self._min_pulse_id_le = QtGui.QLineEdit(str(min_pulse_id))
        self._min_pulse_id_le.setEnabled(False)
        self._max_pulse_id_le = QtGui.QLineEdit(str(max_pulse_id))
        self._max_pulse_id_le.setValidator(self._pulse_id_validator)

        self._vip_pulse_id1_le = QtGui.QLineEdit(str(vip_pulse_id1))
        self._vip_pulse_id1_le.setValidator(self._pulse_id_validator)

        self._vip_pulse_id2_le = QtGui.QLineEdit(str(vip_pulse_id2))
        self._vip_pulse_id2_le.setValidator(self._pulse_id_validator)

        self._non_reconfigurable_widgets = [
            self._max_pulse_id_le,
        ]

        self.initUI()
        self.initConnections()

        self.setFixedHeight(self.minimumSizeHint().height())

    def initUI(self):
        """Overload."""
        layout = QtGui.QGridLayout()
        AR = QtCore.Qt.AlignRight

        if self._pulse_resolved:
            layout.addWidget(QtGui.QLabel("Min. pulse ID: "), 0, 0, AR)
            layout.addWidget(self._min_pulse_id_le, 0, 1)
            layout.addWidget(QtGui.QLabel("Max. pulse ID: "), 0, 2, AR)
            layout.addWidget(self._max_pulse_id_le, 0, 3)

            layout.addWidget(QtGui.QLabel("VIP pulse ID 1: "), 1, 0, AR)
            layout.addWidget(self._vip_pulse_id1_le, 1, 1)
            layout.addWidget(QtGui.QLabel("VIP pulse ID 2: "), 1, 2, AR)
            layout.addWidget(self._vip_pulse_id2_le, 1, 3)

        self.setLayout(layout)

    def initConnections(self):
        mediator = self._mediator

        self._vip_pulse_id1_le.returnPressed.connect(
            lambda: mediator.vip_pulse_id1_sgn.emit(
                int(self._vip_pulse_id1_le.text())))

        self._vip_pulse_id2_le.returnPressed.connect(
            lambda: mediator.vip_pulse_id2_sgn.emit(
                int(self._vip_pulse_id2_le.text())))

        mediator.vip_pulse_ids_connected_sgn.connect(self.updateVipPulseIDs)

    def updateSharedParameters(self):
        """Override"""
        # Upper bound is not included, Python convention
        pulse_id_range = (int(self._min_pulse_id_le.text()),
                          int(self._max_pulse_id_le.text()) + 1)
        self._mediator.pulse_id_range_sgn.emit(*pulse_id_range)

        return True

    def updateVipPulseIDs(self):
        """Called when OverviewWindow is opened."""
        self._vip_pulse_id1_le.returnPressed.emit()
        self._vip_pulse_id2_le.returnPressed.emit()
