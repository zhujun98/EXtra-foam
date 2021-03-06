"""
Distributed under the terms of the BSD 3-Clause License.

The full license is in the file LICENSE, distributed with this software.

Author: Jun Zhu <jun.zhu@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
import abc

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QGroupBox, QLineEdit, QAbstractSpinBox
)

from .smart_widgets import SmartBoundaryLineEdit, SmartSliceLineEdit
from ..gui_helpers import parse_slice_inv
from ..mediator import Mediator
from ...database import MetaProxy
from ...logger import logger


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
    def loadMetaData(self):
        """Load metadata from Redis and set this control widget."""
        # raise NotImplementedError
        pass

    @abc.abstractmethod
    def onStart(self):
        raise NotImplementedError

    @abc.abstractmethod
    def onStop(self):
        raise NotImplementedError

    def _updateWidgetValue(self, widget, config, key, *, cast=None):
        """Update widget value from meta data."""
        value = self._getMetaData(config, key)
        if value is None:
            return

        if cast is not None:
            value = cast(value)

        if isinstance(widget, QCheckBox):
            widget.setChecked(value == 'True')
        elif isinstance(widget, SmartBoundaryLineEdit):
            widget.setText(value[1:-1])
        elif isinstance(widget, SmartSliceLineEdit):
            widget.setText(parse_slice_inv(value))
        elif isinstance(widget, QLineEdit):
            widget.setText(value)
        elif isinstance(widget, QAbstractSpinBox):
            widget.setValue(value)
        else:
            logger.error(f"Unknown widget type: {type(widget)}")

    @staticmethod
    def _getMetaData(config, key):
        """Convienient function to get metadata and capture key error.

        :param dict config: config dictionary.
        :param str key: meta data key.
        """
        try:
            return config[key]
        except KeyError:
            # This happens when loading metadata in a new version with
            # a config file in the old version.
            logger.warning(f"Meta data key not found: {key}")


class _AbstractCtrlWidget(QFrame, _AbstractCtrlWidgetMixin):

    def __init__(self, *,
                 pulse_resolved=True,
                 require_geometry=True,
                 parent=None):
        """Initialization.

        :param bool pulse_resolved: whether the related data is
            pulse-resolved or not.
        :param bool require_geometry: whether the detector requires a
            geometry to assemble its modules.
        """
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self._mediator = Mediator()
        self._meta = MetaProxy()

        # widgets whose values are not allowed to change after the "run"
        # button is clicked
        self._non_reconfigurable_widgets = []

        self._pulse_resolved = pulse_resolved
        self._require_geometry = require_geometry

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

    def __init__(self, title, *,
                 pulse_resolved=True, require_geometry=True, parent=None):
        """Initialization.

        :param bool pulse_resolved: whether the related data is
            pulse-resolved or not.
        :param bool require_geometry: whether the detector requires a
            geometry to assemble its modules.
        """
        super().__init__(title, parent=parent)
        self.setStyleSheet(self.GROUP_BOX_STYLE_SHEET)

        self._mediator = Mediator()
        self._meta = MetaProxy()

        # widgets whose values are not allowed to change after the "run"
        # button is clicked
        self._non_reconfigurable_widgets = []

        self._pulse_resolved = pulse_resolved
        self._require_geometry = require_geometry

    def onStart(self):
        for widget in self._non_reconfigurable_widgets:
            widget.setEnabled(False)

    def onStop(self):
        for widget in self._non_reconfigurable_widgets:
            widget.setEnabled(True)
