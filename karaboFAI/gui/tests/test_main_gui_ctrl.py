import unittest
from unittest.mock import patch, MagicMock
import math
import tempfile
import os

import numpy as np

from PyQt5 import QtCore
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtCore import Qt

from karabo_data.geometry import LPDGeometry

from karaboFAI.config import _Config, ConfigWrapper
from karaboFAI.gui import mkQApp
from karaboFAI.services import Fai
from karaboFAI.pipeline.data_model import ImageData, ProcessedData
from karaboFAI.config import (
    config, AiNormalizer, CorrelationFom, DataSource, Projection1dNormalizer,
    PumpProbeMode, PumpProbeType, RoiFom
)


class TestMainGui(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # do not use the config file in the current computer
        _Config._filename = os.path.join(tempfile.mkdtemp(), "config.json")
        ConfigWrapper()  # ensure file

        cls.fai = Fai('LPD')
        cls.fai.init()
        cls.app = mkQApp()
        cls.gui = cls.fai.gui
        cls.scheduler = cls.fai._scheduler
        cls.bridge = cls.fai._bridge

        cls._actions = cls.gui._tool_bar.actions()
        cls._start_action = cls._actions[0]
        cls._stop_action = cls._actions[1]
        cls._imagetool_action = cls._actions[2]
        cls._pp_action = cls._actions[4]
        cls._correlation_action = cls._actions[5]
        cls._xas_action = cls._actions[6]
        cls._pulsed_ai_action = cls._actions[7]

    @classmethod
    def tearDownClass(cls):
        cls.fai.shutdown()
        cls.gui.close()

    def setUp(self):
        ImageData.clear()

    def testAnalysisCtrlWidget(self):
        widget = self.gui.analysis_ctrl_widget
        geom_widget = self.gui.geometry_ctrl_widget
        scheduler = self.scheduler
        assembler = scheduler._image_assembler
        proc = scheduler._ai_proc

        # --------------------------
        # test setting VIP pulse IDs
        # --------------------------

        self._pulsed_ai_action.trigger()
        window = list(self.gui._windows.keys())[-1]

        # default values
        vip_pulse_id1 = int(widget._vip_pulse_id1_le.text())
        self.assertEqual(vip_pulse_id1, window._vip1_ai.pulse_id)
        self.assertEqual(vip_pulse_id1, window._vip1_img.pulse_id)
        vip_pulse_id2 = int(widget._vip_pulse_id2_le.text())
        self.assertEqual(vip_pulse_id2, window._vip2_ai.pulse_id)
        self.assertEqual(vip_pulse_id2, window._vip2_img.pulse_id)

        # set new values
        vip_pulse_id1 = 10
        widget._vip_pulse_id1_le.setText(str(vip_pulse_id1))
        self.assertEqual(vip_pulse_id1, window._vip1_ai.pulse_id)
        self.assertEqual(vip_pulse_id1, window._vip1_img.pulse_id)

        vip_pulse_id2 = 20
        widget._vip_pulse_id2_le.setText(str(vip_pulse_id2))
        self.assertEqual(vip_pulse_id2, window._vip2_ai.pulse_id)
        self.assertEqual(vip_pulse_id2, window._vip2_img.pulse_id)

        # test params sent to AzimuthalIntegrationProcessor

        proc.update()
        self.assertAlmostEqual(config['SAMPLE_DISTANCE'], proc.sample_distance)
        self.assertAlmostEqual(config['PHOTON_ENERGY'], proc.photon_energy)

        widget._photon_energy_le.setText("12.4")
        widget._sample_dist_le.setText("0.3")

        proc.update()
        self.assertAlmostEqual(12.4, proc.photon_energy)
        self.assertAlmostEqual(0.3, proc.sample_distance)

        widget.updateSharedParameters()
        geom_widget.updateSharedParameters()
        assembler.update()
        self.assertEqual((0, 2700), assembler._pulse_id_range)

        widget._max_pulse_id_le.setText("1000")
        widget.updateSharedParameters()
        assembler.update()
        self.assertEqual((0, 1001), assembler._pulse_id_range)

    def testAzimuthalIntegCtrlWidget(self):
        widget = self.gui.azimuthal_integ_ctrl_widget
        scheduler = self.scheduler
        proc = scheduler._ai_proc

        proc.update()
        self.assertFalse(proc.enable_pulsed_ai)
        default_integ_method = 'BBox'
        self.assertEqual(proc.integ_method, default_integ_method)
        default_normalizer = AiNormalizer.AUC
        self.assertEqual(proc.normalizer, default_normalizer)
        self.assertEqual(config["AZIMUTHAL_INTEG_POINTS"],
                         proc.integ_points)
        default_integ_range = tuple(config["AZIMUTHAL_INTEG_RANGE"])
        self.assertTupleEqual(tuple(config["AZIMUTHAL_INTEG_RANGE"]),
                              proc.integ_range)
        self.assertTupleEqual(default_integ_range, proc.auc_range)
        self.assertTupleEqual(default_integ_range, proc.fom_integ_range)
        self.assertEqual(config["CENTER_X"], proc.integ_center_x)
        self.assertEqual(config["CENTER_Y"], proc.integ_center_y)

        widget._pulsed_integ_cb.setChecked(True)
        itgt_method = 'nosplit_csr'
        widget._itgt_method_cb.setCurrentText(itgt_method)
        ai_normalizer = AiNormalizer.ROI2
        widget._normalizers_cb.setCurrentIndex(ai_normalizer)
        widget._integ_pts_le.setText(str(1024))
        widget._integ_range_le.setText("0.1, 0.2")
        widget._auc_range_le.setText("0.2, 0.3")
        widget._fom_integ_range_le.setText("0.3, 0.4")
        widget._cx_le.setText("-1000")
        widget._cy_le.setText("1000")

        proc.update()
        self.assertTrue(proc.enable_pulsed_ai)
        self.assertEqual(proc.integ_method, itgt_method)
        self.assertEqual(proc.normalizer, ai_normalizer)
        self.assertEqual(1024, proc.integ_points)
        self.assertTupleEqual((0.1, 0.2), proc.integ_range)
        self.assertTupleEqual((0.2, 0.3), proc.auc_range)
        self.assertTupleEqual((0.3, 0.4), proc.fom_integ_range)
        self.assertEqual(-1000, proc.integ_center_x)
        self.assertEqual(1000, proc.integ_center_y)

    def testRoiCtrlWidget(self):
        widget = self.gui.roi_ctrl_widget
        proc = self.scheduler._roi_proc
        proc.update()

        # test default reconfigurable values
        self.assertEqual(np.sum, proc.roi_fom_handler)
        self.assertEqual(Projection1dNormalizer.AUC, proc.proj1d_normalizer)
        self.assertEqual((0, math.inf), proc.proj1d_fom_integ_range)
        self.assertEqual((0, math.inf), proc.proj1d_auc_range)

        # test setting new values
        widget._roi_fom_cb.setCurrentText('mean')
        widget._fom_integ_range_le.setText("10, 20")
        widget._auc_range_le.setText("30, 40")
        proc.update()

        self.assertEqual(np.mean, proc.roi_fom_handler)
        self.assertEqual((10, 20), proc.proj1d_fom_integ_range)
        self.assertEqual((30, 40), proc.proj1d_auc_range)

    def testPumpProbeCtrlWidget(self):
        widget = self.gui.pump_probe_ctrl_widget
        proc = self.scheduler._pp_proc
        proc.update()

        # check default reconfigurable params
        self.assertEqual(1, proc.ma_window)
        self.assertTrue(proc.abs_difference)
        self.assertEqual(PumpProbeType(0), proc.analysis_type)

        # change reconfigurable params
        QTest.mouseClick(widget._abs_difference_cb, Qt.LeftButton,
                         pos=QtCore.QPoint(2, widget._abs_difference_cb.height()/2))
        widget._ma_window_le.setText(str(10))
        new_fom = PumpProbeType.ROI
        widget._analysis_type_cb.setCurrentIndex(new_fom)

        proc.update()

        self.assertFalse(proc.abs_difference)
        self.assertEqual(10, proc.ma_window)
        self.assertEqual(PumpProbeType(new_fom), proc.analysis_type)

        # check default non-reconfigurable params
        self.assertTrue(self.gui.updateSharedParameters())
        proc.update()

        self.assertEqual(PumpProbeMode.UNDEFINED, proc.mode)

        # assign new values
        new_mode = PumpProbeMode.EVEN_TRAIN_ON
        widget._mode_cb.setCurrentIndex(new_mode)
        widget._on_pulse_le.setText('0:10:2')
        widget._off_pulse_le.setText('1:10:2')

        self.assertTrue(self.gui.updateSharedParameters())
        proc.update()

        self.assertEqual(PumpProbeMode(new_mode), proc.mode)
        self.assertListEqual([0, 2, 4, 6, 8], proc.on_pulse_ids)
        self.assertIsInstance(proc.on_pulse_ids[0], int)
        self.assertListEqual([1, 3, 5, 7, 9], proc.off_pulse_ids)
        self.assertIsInstance(proc.off_pulse_ids[0], int)

    def testXasCtrlWidget(self):
        widget = self.gui.xas_ctrl_widget
        proc = self.scheduler._xas_proc

        proc.update()

        # check initial value is set
        self.assertEqual(int(widget._nbins_le.text()), proc.n_bins)

        # set another value
        widget._nbins_le.setText("40")

        proc.update()

        self.assertEqual(40, proc.n_bins)

    @patch.dict(config._data, {"SOURCE_NAME_BRIDGE": ["E", "F", "G"],
                               "SOURCE_NAME_FILE": ["A", "B"]})
    def testDataCtrlWidget(self):
        widget = self.gui.data_ctrl_widget
        scheduler = self.scheduler
        assembler = scheduler._image_assembler
        aggregtor = scheduler._data_aggregator
        bridge = self.bridge
        bridge.update()

        # test passing tcp hostname and port

        hostname = config['SERVER_ADDR']
        port = config['SERVER_PORT']
        self.assertListEqual([f"tcp://{hostname}:{port}"],
                             list(bridge._clients.keys()))

        widget._hostname_le.setText('127.0.0.1')
        widget._port_le.setText('12345')

        bridge.update()
        self.assertListEqual([f"tcp://127.0.0.1:12345"],
                             list(bridge._clients.keys()))

        # test passing data source types and detector source name

        source_type = DataSource.FILE
        widget._source_type_cb.setCurrentIndex(source_type)
        bridge.update()
        scheduler.update()
        assembler.update()
        aggregtor.update()

        self.assertEqual(source_type, assembler._source_type)
        self.assertEqual(source_type, scheduler._source_type)
        self.assertEqual(source_type, bridge._source_type)
        self.assertEqual("A", assembler._detector_source_name)
        items = []
        for i in range(widget._detector_src_cb.count()):
            items.append(widget._detector_src_cb.itemText(i))
        self.assertListEqual(["A", "B"], items)
        self.assertEqual(widget._mono_src_cb.currentText(),
                         scheduler._data_aggregator._mono_src)
        self.assertEqual(widget._xgm_src_cb.currentText(),
                         scheduler._data_aggregator._xgm_src)

        # change source_type from FILE to BRIDGE

        source_type = DataSource.BRIDGE
        widget._source_type_cb.setCurrentIndex(source_type)
        widget._mono_src_cb.setCurrentIndex(1)
        widget._xgm_src_cb.setCurrentIndex(1)

        bridge.update()
        scheduler.update()
        assembler.update()
        aggregtor.update()

        self.assertEqual(source_type, assembler._source_type)
        self.assertEqual(source_type, scheduler._source_type)
        self.assertEqual(source_type, bridge._source_type)
        self.assertEqual("E", assembler._detector_source_name)
        items = []
        for i in range(widget._detector_src_cb.count()):
            items.append(widget._detector_src_cb.itemText(i))
        self.assertListEqual(["E", "F", "G"], items)

        self.assertEqual(widget._mono_src_cb.currentText(),
                         scheduler._data_aggregator._mono_src)
        self.assertEqual(widget._xgm_src_cb.currentText(),
                         scheduler._data_aggregator._xgm_src)

    def testGeometryCtrlWidget(self):
        widget = self.gui.geometry_ctrl_widget
        scheduler = self.scheduler

        widget._geom_file_le.setText(config["GEOMETRY_FILE"])

        self.assertTrue(self.gui.updateSharedParameters())

        self.assertIsInstance(scheduler._image_assembler._geom, LPDGeometry)

    def testCorrelationCtrlWidget(self):
        widget = self.gui.correlation_ctrl_widget
        scheduler = self.scheduler
        proc = scheduler._correlation_proc
        self._correlation_action.trigger()
        window = list(self.gui._windows.keys())[-1]

        proc.update()
        self.assertEqual(CorrelationFom(0), proc.fom_type)

        new_fom = CorrelationFom.ROI1
        widget._fom_type_cb.setCurrentIndex(new_fom)
        proc.update()
        self.assertEqual(CorrelationFom(new_fom),
                         scheduler._correlation_proc.fom_type)

        # test default FOM type
        self.assertTrue(self.gui.updateSharedParameters())

        # test the correlation param table
        expected_correlations = []
        for i in range(widget._n_params):
            widget._table.cellWidget(i, 0).setCurrentIndex(1)

            proc.update()
            for item in expected_correlations:
                self.assertTrue(hasattr(ProcessedData(1).correlation, item))

            widget._table.cellWidget(i, 1).setCurrentIndex(1)
            correlation = f'correlation{i+1}'
            expected_correlations.append(correlation)

            resolution = (i+1)*5 if i < 2 else 0.0
            resolution_le = widget._table.cellWidget(i, 3)
            resolution_le.setText(str(resolution))

            proc.update()
            if resolution > 0:
                _, _, info = getattr(ProcessedData(1).correlation, correlation)
                self.assertEqual(resolution, info['resolution'])
            else:
                _, _, info = getattr(ProcessedData(1).correlation, correlation)
                self.assertNotIn('resolution', info)

        # test data visualization
        # the upper two plots have error bars
        data = ProcessedData(1, images=np.arange(480).reshape(120, 2, 2))
        for i in range(1000):
            data.correlation.correlation1 = (int(i/5), 100*i)
            data.correlation.correlation2 = (int(i/5), -100*i)
            data.correlation.correlation3 = (i, i+1)
            data.correlation.correlation4 = (i, -i)
        self.gui._data.set(data)
        window.update()
        self.app.processEvents()

        # change the resolutions
        for i in range(widget._n_params):
            resolution = (i+1)*5 if i >= 2 else 0.0
            resolution_le = widget._table.cellWidget(i, 3)
            resolution_le.setText(str(resolution))

        # the data is cleared after the resolutions were changed
        # now the lower two plots have error bars but the upper ones do not
        for i in range(1000):
            data.correlation.correlation3 = (int(i/5), 100*i)
            data.correlation.correlation4 = (int(i/5), -100*i)
            data.correlation.correlation1 = (i, i+1)
            data.correlation.correlation2 = (i, -i)
        self.gui._data.set(data)
        window.update()
        self.app.processEvents()
