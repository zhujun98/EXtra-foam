Data Analysis with karaboFAI
============================


To start **karaboFAI** on online or `Maxwell` clusters:

.. code-block:: bash

    # stable version
    module load exfel exfel_anaconda3
    karaboFAI DETECTOR_NAME

Valid detectors are `AGIPD`, `LPD`, `JungFrau` and `FastCCD`.

You are also encouraged to try the latest version (more features). However, the
latest version is **not** supported by OCD.

.. code-block:: bash

    # latest version
    module load exfel exfel_anaconda3/beta
    karaboFAI DETECTOR_NAME

.. note::
    It usually takes some time to start **karaboFAI** for the first time! This
    is actually an issue related to the infrastructure and not because
    **karaboFAI** is slow.

.. note::
    In order to have a better experience with **karaboFAI** on the `Maxwell` cluster,
    you should need FastX2_ at max-display_. There is also a link for downloading
    the desktop client on the bottom-right corner when you opened max-display_. For
    more details, please refer to the official website for FastX2_ at DESY.

.. _FastX2: https://confluence.desy.de/display/IS/FastX2
.. _max-display: https://max-display.desy.de:3443/


Data analysis in real time
--------------------------


For real-time data analysis, the (calibrated) data is streamed via a
`ZMQ bridge`, which is a `Karabo` device (`PipeToZeroMQ`) running inside the control network.
Normally, the user should not modify ``Hostname``, ``Port`` and ``Source`` in
the ``Data source`` panel.

.. image:: images/data_source_real_time.png
   :width: 300

.. list-table:: Suggested online clusters
   :header-rows: 1

   * - Instrument
     - Alias
     - DNS primary name

   * - SPB
     - sa1-br-onc-comp-spb
     - exflonc05
   * - FXE
     - sa1-br-onc-comp-fxe
     - exflonc12
   * - SCS
     - sa1-br-kc-comp-1
     - exflonc13
   * - SQS
     - sa1-br-kc-comp-3
     - exflonc15

Data analysis with files
------------------------

**karaboFAI** can be used to replay the experiment with files.


The data is streamed from files after the ``Serve`` button is clicked. The user
is free to use any available ``port``. ``Hostname`` should be `localhost` and
the user needs to specify the full path of the directory which contains the
(calibrated) files.

.. image:: images/data_source_from_file.png
   :width: 300

.. list-table:: Example files
   :header-rows: 1

   * - Detector
     - File directory

   * - AGIPD
     - /gpfs/exfel/exp/XMPL/201750/p700000/proc/r0006
   * - LPD
     - /gpfs/exfel/exp/FXE/201701/p002026/proc/r0078
   * - JungFrau
     - /gpfs/exfel/exp/FXE/201801/p002118/proc/r0143
   * - FastCCD
     - /gpfs/exfel/exp/SCS/201802/p002170/proc/r0141