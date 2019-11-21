"""
Distributed under the terms of the BSD 3-Clause License.

The full license is in the file LICENSE, distributed with this software.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
import abc
from collections import OrderedDict

from PyQt5.QtWidgets import QFrame, QGroupBox

from ..mediator import Mediator


class _AbstractCtrlWidgetMixin:
    @abc.abstractmethod
    def initUI(self):
        """Initialization of UI."""
        raise NotImplementedError

    @abc.abstractmethod
    def initConnections(self):
        """Initialization of signal-slot connections."""
        raise NotImplementedError

    @abc.abstractmethod
    def updateMetaData(self):
        """Update metadata belong to this control widget.

        :returns bool: True if all metadata successfully parsed
            and emitted, otherwise False.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def onStart(self):
        raise NotImplementedError

    @abc.abstractmethod
    def onStop(self):
        raise NotImplementedError


class _AbstractCtrlWidget(QFrame, _AbstractCtrlWidgetMixin):
    def __init__(self, *, pulse_resolved=True, parent=None):
        """Initialization.

        :param bool pulse_resolved: whether the related data is
            pulse-resolved or not.
        """
        super().__init__(parent=parent)

        self._mediator = Mediator()

        # widgets whose values are not allowed to change after the "run"
        # button is clicked
        self._non_reconfigurable_widgets = []

        # whether the related detector is pulse resolved or not
        self._pulse_resolved = pulse_resolved

        self.setFrameStyle(QFrame.StyledPanel)

    def onStart(self):
        for widget in self._non_reconfigurable_widgets:
            widget.setEnabled(False)

    def onStop(self):
        for widget in self._non_reconfigurable_widgets:
            widget.setEnabled(True)


class _AbstractGroupBoxCtrlWidget(QGroupBox, _AbstractCtrlWidgetMixin):
    GROUP_BOX_STYLE_SHEET = 'QGroupBox:title {'\
                            'color: #8B008B;' \
                            'border: 1px;' \
                            'subcontrol-origin: margin;' \
                            'subcontrol-position: top left;' \
                            'padding-left: 10px;' \
                            'padding-top: 10px;' \
                            'margin-top: 0.0em;}'
    class SourcePropertyItem:
        def __init__(self, device_ids=None, properties=None):
            self.device_ids = device_ids if device_ids is not None else []
            self.properties = properties if properties is not None else []

    # Data categories for different topics
    _TOPIC_DATA_CATEGORIES = {
        "UNKNOWN": OrderedDict({
            "": SourcePropertyItem(),
            "Train ID": SourcePropertyItem(
                device_ids=["", "Any"],
                properties=["timestamp.tid"]
            ),
            "User defined": SourcePropertyItem()}),
        "SPB": OrderedDict({
            "": SourcePropertyItem(),
            "Train ID": SourcePropertyItem(
                device_ids=["", "Any"],
                properties=["timestamp.tid"]
            ),
            "User defined": SourcePropertyItem(),
        }),
        "FXE": OrderedDict({
            "": SourcePropertyItem(),
            "Train ID": SourcePropertyItem(
                device_ids=["", "Any"],
                properties=["timestamp.tid"]
            ),
            "User defined": SourcePropertyItem(),
            "Motor": SourcePropertyItem(
                device_ids=[
                    "",
                    "FXE_SMS_USR/MOTOR/UM01",
                    "FXE_SMS_USR/MOTOR/UM02",
                    "FXE_SMS_USR/MOTOR/UM04",
                    "FXE_SMS_USR/MOTOR/UM05",
                    "FXE_SMS_USR/MOTOR/UM13",
                    "FXE_AUXT_LIC/DOOCS/PPLASER",
                    "FXE_AUXT_LIC/DOOCS/PPODL",
                ],
                properties=["actualPosition"],
            ),
        }),
        "SCS": OrderedDict({
            "": SourcePropertyItem(),
            "Train ID": SourcePropertyItem(
                device_ids=["", "Any"],
                properties=["timestamp.tid"]
            ),
            "User defined": SourcePropertyItem(),
            "MonoChromator": SourcePropertyItem(
                device_ids=[
                    "",
                    "SA3_XTD10_MONO/MDL/PHOTON_ENERGY"
                ],
                properties=["actualEnergy"],
            ),
            "Motor": SourcePropertyItem(
                device_ids=[
                    "",
                    "SCS_ILH_LAS/PHASESHIFTER/DOOCS",
                    "SCS_ILH_LAS/DOOCS/PP800_PHASESHIFTER",
                    "SCS_ILH_LAS/MOTOR/LT3",
                ],
                properties=["actualPosition"],
            ),
            "MAGNET": SourcePropertyItem(
                device_ids=[
                    "",
                    "SCS_CDIFFT_MAG/SUPPLY/CURRENT",
                ],
                properties=["actualCurrent"],
            ),
        }),
        "SQS": OrderedDict({
            "": SourcePropertyItem(),
            "Train ID": SourcePropertyItem(
                device_ids=["", "Any"],
                properties=["timestamp.tid"]
            ),
            "User defined": SourcePropertyItem(),
        }),
        "MID": OrderedDict({
            "": SourcePropertyItem(),
            "Train ID": SourcePropertyItem(
                device_ids=["", "Any"],
                properties=["timestamp.tid"]
            ),
            "User defined": SourcePropertyItem(),
        }),
        "HED": OrderedDict({
            "": SourcePropertyItem(),
            "Train ID": SourcePropertyItem(
                device_ids=["", "Any"],
                properties=["timestamp.tid"]
            ),
            "User defined": SourcePropertyItem(),
        }),
    }

    def __init__(self, title, *, pulse_resolved=True, parent=None):
        """Initialization.

        :param bool pulse_resolved: whether the related data is
            pulse-resolved or not.
        """
        super().__init__(title, parent=parent)
        self.setStyleSheet(self.GROUP_BOX_STYLE_SHEET)

        self._mediator = Mediator()

        # widgets whose values are not allowed to change after the "run"
        # button is clicked
        self._non_reconfigurable_widgets = []

        # whether the related detector is pulse resolved or not
        self._pulse_resolved = pulse_resolved

    def onStart(self):
        for widget in self._non_reconfigurable_widgets:
            widget.setEnabled(False)

    def onStop(self):
        for widget in self._non_reconfigurable_widgets:
            widget.setEnabled(True)
