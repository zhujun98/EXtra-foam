"""
Distributed under the terms of the BSD 3-Clause License.

The full license is in the file LICENSE, distributed with this software.

Author: Jun Zhu <jun.zhu@xfel.eu>, Ebad Kamil <ebad.kamil@xfel.eu>
Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
All rights reserved.
"""
from collections import OrderedDict
import functools

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QComboBox, QGridLayout, QHeaderView, QLabel, QPushButton, QTableWidget
)

from .base_ctrl_widgets import _AbstractGroupBoxCtrlWidget
from .smart_widgets import SmartLineEdit
from ...config import AnalysisType, config

_N_PARAMS = 2  # maximum number of correlated parameters
_DEFAULT_RESOLUTION = "0.0"


class CorrelationCtrlWidget(_AbstractGroupBoxCtrlWidget):
    """Widget for setting up correlation analysis parameters."""

    _analysis_types = OrderedDict({
        "": AnalysisType.UNDEFINED,
        "pump-probe": AnalysisType.PUMP_PROBE,
        "ROI FOM": AnalysisType.ROI_FOM,
        "ROI proj": AnalysisType.ROI_PROJ,
        "azimuthal integ": AnalysisType.AZIMUTHAL_INTEG,
    })

    def __init__(self, *args, **kwargs):
        super().__init__("Correlation setup", *args, **kwargs)

        self._analysis_type_cb = QComboBox()
        for v in self._analysis_types:
            self._analysis_type_cb.addItem(v)

        self._reset_btn = QPushButton("Reset")

        self._table = QTableWidget()

        self.initUI()
        self.initConnections()

    def initUI(self):
        """Overload."""
        layout = QGridLayout()
        AR = Qt.AlignRight

        layout.addWidget(QLabel("Analysis type: "), 0, 0, AR)
        layout.addWidget(self._analysis_type_cb, 0, 1)
        layout.addWidget(self._reset_btn, 0, 5, AR)
        layout.addWidget(self._table, 1, 0, 1, 6)

        self.setLayout(layout)

        self.initParamTable()

    def initConnections(self):
        """Overload."""
        mediator = self._mediator

        self._analysis_type_cb.currentTextChanged.connect(
            lambda x: mediator.onCorrelationAnalysisTypeChange(
                self._analysis_types[x]))
        self._analysis_type_cb.currentTextChanged.emit(
            self._analysis_type_cb.currentText())

        self._reset_btn.clicked.connect(mediator.onCorrelationReset)

    def initParamTable(self):
        """Initialize the correlation parameter table widget."""
        table = self._table

        n_row = _N_PARAMS
        n_col = 4

        table.setColumnCount(n_col)
        table.setRowCount(n_row)
        table.setHorizontalHeaderLabels([
            'Category', 'Karabo Device ID', 'Property Name', 'Resolution'])
        table.setVerticalHeaderLabels([str(i+1) for i in range(_N_PARAMS)])
        for i_row in range(_N_PARAMS):
            combo = QComboBox()
            for t in self._TOPIC_DATA_CATEGORIES[config["TOPIC"]].keys():
                combo.addItem(t)
            table.setCellWidget(i_row, 0, combo)
            combo.currentTextChanged.connect(
                functools.partial(self.onCategoryChange, i_row))

            for i_col in range(1, 3):
                widget = SmartLineEdit()
                table.setCellWidget(i_row, i_col, widget)
                widget.setReadOnly(True)

            widget = self._get_default_resolution_widget()
            table.setCellWidget(i_row, 3, widget)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)

        header = table.verticalHeader()
        for i in range(n_row):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        header_height = self._table.horizontalHeader().height()
        self._table.setMinimumHeight(header_height * (_N_PARAMS + 1.5))
        self._table.setMaximumHeight(header_height * (_N_PARAMS + 2.5))

    @pyqtSlot(str)
    def onCategoryChange(self, i_row, text):
        resolution_le = self._get_default_resolution_widget()

        # i_row is the row number in the QTableWidget
        if not text or text == "User defined":
            # '' or 'User defined'
            device_id_le = SmartLineEdit()
            property_le = SmartLineEdit()

            if not text:
                device_id_le.setReadOnly(True)
                property_le.setReadOnly(True)
            else:
                device_id_le.returnPressed.connect(functools.partial(
                    self.onCorrelationParamChangeLe, i_row))
                property_le.returnPressed.connect(functools.partial(
                    self.onCorrelationParamChangeLe, i_row))
                resolution_le.returnPressed.connect(functools.partial(
                    self.onCorrelationParamChangeLe, i_row))

            self._table.setCellWidget(i_row, 1, device_id_le)
            self._table.setCellWidget(i_row, 2, property_le)
            self._table.setCellWidget(i_row, 3, resolution_le)

            self.onCorrelationParamChangeLe(i_row)
        else:
            combo_device_ids = QComboBox()
            for device_id in self._TOPIC_DATA_CATEGORIES[config["TOPIC"]][text].device_ids:
                combo_device_ids.addItem(device_id)

            combo_device_ids.currentTextChanged.connect(functools.partial(
                self.onCorrelationParamChangeCb, i_row))
            self._table.setCellWidget(i_row, 1, combo_device_ids)

            combo_properties = QComboBox()
            for ppt in self._TOPIC_DATA_CATEGORIES[config["TOPIC"]][text].properties:
                combo_properties.addItem(ppt)
            combo_properties.currentTextChanged.connect(functools.partial(
                self.onCorrelationParamChangeCb, i_row))
            self._table.setCellWidget(i_row, 2, combo_properties)

            resolution_le.returnPressed.connect(functools.partial(
                self.onCorrelationParamChangeCb, i_row))
            self._table.setCellWidget(i_row, 3, resolution_le)

            self.onCorrelationParamChangeCb(i_row)

    @pyqtSlot()
    def onCorrelationParamChangeLe(self, i_row):
        device_id = self._table.cellWidget(i_row, 1).text()
        ppt = self._table.cellWidget(i_row, 2).text()
        res = float(self._table.cellWidget(i_row, 3).text())

        self._mediator.onCorrelationParamChange(
            (i_row+1, device_id, ppt, res))

    @pyqtSlot(str)
    def onCorrelationParamChangeCb(self, i_row):
        device_id = self._table.cellWidget(i_row, 1).currentText()
        ppt = self._table.cellWidget(i_row, 2).currentText()
        res = float(self._table.cellWidget(i_row, 3).text())

        self._mediator.onCorrelationParamChange(
            (i_row+1, device_id, ppt, res))

    def updateMetaData(self):
        """Overload."""
        self._analysis_type_cb.currentTextChanged.emit(
            self._analysis_type_cb.currentText())

        for i_row in range(_N_PARAMS):
            category = self._table.cellWidget(i_row, 0).currentText()
            if not category or category == "User defined":
                self.onCorrelationParamChangeLe(i_row)
            else:
                self.onCorrelationParamChangeCb(i_row)
        return True

    def _get_default_resolution_widget(self):
        resolution_le = SmartLineEdit(_DEFAULT_RESOLUTION)
        validator = QDoubleValidator()
        validator.setBottom(0.0)
        resolution_le.setValidator(validator)
        return resolution_le