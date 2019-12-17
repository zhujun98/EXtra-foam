MAIN GUI
========

.. _pyFAI: https://github.com/silx-kit/pyFAI
.. _karabo_data: https://github.com/European-XFEL/karabo_data

.. _nanmean: https://docs.scipy.org/doc/numpy/reference/generated/numpy.nanmean.html


The main GUI of **EXtra-foam** is divided into several control panels grouped
by functionality and a log window.

.. image:: images/MainGUI.png
   :width: 800

Important concepts:

.. _AnalysisType:

- **Analysis type**:

Each analysis type starts from an (ROI) image and will generate a FOM (figure-of-merit) and a VFOM
(vector figure-of-merit). Take the analysis type *ROI1 - ROI2 (proj)* for example, it starts
from the image which is the subtraction of ROI1 and ROI2. The VFOM is the projection of this image in
the x or y direction, and the FOM the sum of the absolute VFOM.

.. list-table::
   :header-rows: 1

   * - Type
     - Description
     - VFOM
     - FOM

   * - *pump-probe*
     - See *Pump-probe setup*.
     - VFOM (on) minus VFOM (off).
     - Sum of the (absolute) on-off VFOM.

   * - *ROI1*
     - Sum ROI1.
     - NA
     - Sum of the pixel values within ROI1.

   * - *ROI2*
     - Sum ROI2.
     - NA
     - Sum of the pixel values within ROI2.

   * - *ROI1 - ROI2*
     - Subtract of two ROI regions.
     - NA
     - Sum of the pixel values within ROI1 - ROI2 (ROI1 and ROI2 must have the same shape).

   * - *ROI1 + ROI2*
     - Sum of two ROI regions.
     - NA
     - Sum of the pixel values within ROI1 + ROI2 (ROI1 and ROI2 must have the same shape).

   * - *ROI1 (proj)*
     - 1D projection in x/y direction of ROI1.
     - Projection of ROI1 in the x/y direction.
     - Sum of the absolute projection.

   * - *ROI2 (proj)*
     - 1D projection in x/y direction of ROI2.
     - Projection of ROI2 in the x/y direction.
     - Sum of the absolute projection.

   * - *ROI1 - ROI2 (proj)*
     - 1D projection in x/y direction of the subtraction of two ROI regions.
     - Projection of ROI1 - ROI2 in the x/y direction.
     - Sum of the absolute projection.

   * - *ROI1 + ROI2 (proj)*
     - 1D projection in x/y direction of the sum of two ROI regions.
     - Projection of ROI1 + ROI2 in the x/y direction.
     - Sum of the absolute projection.

   * - *azimuthal integ*
     - Azimuthal integration of average (pulse) image(s) in a train.
     - Azimuthal integration scattering curve.
     - Sum of the (absolute) scattering curve.

Data source
___________

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *Data streamed from*       | Receiving the data from                                            |
|                            |                                                                    |
|                            | - *ZeroMQ bridge*: mainly used for real-time analysis. The data    |
|                            |   will be sent from a *PipeToZeroMQ* Karabo device;                |
|                            |                                                                    |
|                            | - *run directory*: used for replaying the experiment.              |
+----------------------------+--------------------------------------------------------------------+
| *Hostname*                 | Hostname of the data source.                                       |
+----------------------------+--------------------------------------------------------------------+
| *Port*                     | Port number of the data source.                                    |
+----------------------------+--------------------------------------------------------------------+

In the data source tree, one can select which sources (*Source name* and *Property*) are required
in the analysis. The available sources are monitored and displayed in the *Available sources*
window below.

Further filtering operations are provided for each data source if applicable.

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *Pulse slicer*             | The input will be used to construct a *slice* object in Python     |
|                            | which is used to select the specified pulse pattern in a train.    |
+----------------------------+--------------------------------------------------------------------+
| *Value range*              | Value range filter of the corresponding source.                    |
+----------------------------+--------------------------------------------------------------------+


General analysis
________________


Global setup
""""""""""""

Define analysis parameters used globally.

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *POI index 1*              | Index of the first pulse of interest (POI). It is used for         |
|                            | visualizing a single image in the *Pulse-of-interest* window. **If |
|                            | 'Pulse slicer' is used to slice a portion of the pulses in the     |
|                            | train, this index is indeed the index of the pulse in the sliced   |
|                            | train**. *Pulse-resolved detector only.*                           |
+----------------------------+--------------------------------------------------------------------+
| *POI index 2*              | Index of the 2nd POI pulse. *Pulse-resolved detector only.*        |
+----------------------------+--------------------------------------------------------------------+
| *M.A. window*              | Moving average window size. If the moving average window size is   |
|                            | larger than 1, moving average will be applied to all the           |
|                            | registered analysis types. If the new window size is smaller than  |
|                            | the old one, the moving average calculation will start from the    |
|                            | scratch.                                                           |
+----------------------------+--------------------------------------------------------------------+
| Reset M.A.                 | Reset the moving average counts of all registered analysis types.  |
+----------------------------+--------------------------------------------------------------------+

Pump-probe setup
""""""""""""""""

In the *pump-probe* analysis, the average (nanmean_) images of the on- and off- pulses are
calculated by

.. math::

   \bar{I}_{on} = \Sigma I_{on} / N_{on}

   \bar{I}_{off} = \Sigma I_{off} / N_{off} .

Then, moving averages of VFOM (on) and VFOM (off) for :math:`\bar{I}_{on}` and :math:`\bar{I}_{off}`
will be calculated, respectively, depending on the specified analysis type. The VFOM of *pump-probe*
analysis is given by VFOM (on) - VFOM (off).

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *On/off mode*              | Pump-probe analysis mode:                                          |
|                            |                                                                    |
|                            | - *predefined off*:                                                |
|                            |                                                                    |
|                            |   On-pulses will be taken from each train while the 'off'          |
|                            |   (reference image) is specified in the ImageTool.                 |
|                            |                                                                    |
|                            | - *same train*:                                                    |
|                            |                                                                    |
|                            |   On-pulses and off-pulses will be taken from the same train. Not  |
|                            |   applicable to train-resolved detectors.                          |
|                            |                                                                    |
|                            | - *even\/odd*:                                                     |
|                            |                                                                    |
|                            |   On-pulses will be taken from trains with even train IDs while    |
|                            |   off-pulses will be taken from trains with odd train IDs.         |
|                            |                                                                    |
|                            | - *odd\/even*:                                                     |
|                            |                                                                    |
|                            |   On-pulses will be taken from trains with odd train IDs while     |
|                            |   off-pulses will be taken from trains with even train IDs.        |
+----------------------------+--------------------------------------------------------------------+
| *Analysis type*            | See AnalysisType_.                                                 |
+----------------------------+--------------------------------------------------------------------+
| *On-pulse indices*         | Indices of all on-pulses. **If 'Pulse slicer' is used to slice a   |
|                            | portion of the pulses in the train, these indices are indeed the   |
|                            | indices of the pulse in the sliced train**.                        |
|                            | *Pulse-resolved detector only.*                                    |
+----------------------------+--------------------------------------------------------------------+
| *Off-pulse indices*        | Indices of all off-pulses. *Pulse-resolved detector only.*         |
+----------------------------+--------------------------------------------------------------------+
| *FOM from absolute on-off* | If this checkbox is ticked, the FOM will be calculated based on    |
|                            | `\|on - off\|` (default). Otherwise `on - off`.                    |
+----------------------------+--------------------------------------------------------------------+
| Reset                      | Reset the FOM plot in the *Pump-probe window* and the global       |
|                            | moving average count.                                              |
+----------------------------+--------------------------------------------------------------------+


Data reduction setup
""""""""""""""""""""

Apply data reduction by setting the lower and upper boundary of the specified FOM. Currently,
it affects calculating the average of images in a train as well as the averages of images of
ON-/Off- pulses in a train. It only works for pulse-resolved detectors.

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *Analysis type*            | See AnalysisType_.                                                 |
+----------------------------+--------------------------------------------------------------------+
| *FOM range*                | Number of bins of the histogram.                                   |
+----------------------------+--------------------------------------------------------------------+


Statistics setup
""""""""""""""""

Setup the visualization of pulse- / train- resolved statistics analysis.

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *Analysis type*            | See AnalysisType_.                                                 |
+----------------------------+--------------------------------------------------------------------+
| *# of bins*                | Number of bins of the histogram.                                   |
+----------------------------+--------------------------------------------------------------------+
| *Reset*                    | Reset the histogram history.                                       |
+----------------------------+--------------------------------------------------------------------+


Binning setup
"""""""""""""

Setup the visualization of 1D/2D binning of the FOM and VFOM for a certain AnalysisType_.

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *Analysis type*            | See AnalysisType_.                                                 |
+----------------------------+--------------------------------------------------------------------+
| *Mode*                     | The data in each bin will be                                       |
|                            |                                                                    |
|                            | - *average*: averaged;                                             |
|                            |                                                                    |
|                            | - *accumulate*: summed up.                                         |
+----------------------------+--------------------------------------------------------------------+
| *Category*                 | Category of the slow data.                                         |
+----------------------------+--------------------------------------------------------------------+
| *Karabo device ID*         | ID of the Karabo device which produces the slow data.              |
+----------------------------+--------------------------------------------------------------------+
| *Property name*            | Property name in the Karabo device.                                |
+----------------------------+--------------------------------------------------------------------+
| *Value range*              | (Min, max) value of the bins.                                      |
+----------------------------+--------------------------------------------------------------------+
| *# of bins*                | Number of bins.                                                    |
+----------------------------+--------------------------------------------------------------------+
| *Reset*                    | Reset the binning history.                                         |
+----------------------------+--------------------------------------------------------------------+


Correlation setup
"""""""""""""""""

Setup the visualization of correlations of a given FOM with various slow data.

+----------------------------+--------------------------------------------------------------------+
| Input                      | Description                                                        |
+============================+====================================================================+
| *Analysis type*            | See AnalysisType_.                                                 |
+----------------------------+--------------------------------------------------------------------+
| *Category*                 | Category of the slow data.                                         |
+----------------------------+--------------------------------------------------------------------+
| *Karabo device ID*         | ID of the Karabo device which produces the slow data.              |
+----------------------------+--------------------------------------------------------------------+
| *Property name*            | Property name in the Karabo device.                                |
+----------------------------+--------------------------------------------------------------------+
| *Resolution*               | 0 for scattering plot and any positive value for bar plot          |
+----------------------------+--------------------------------------------------------------------+
| *Reset*                    | Reset the correlation history.                                     |
+----------------------------+--------------------------------------------------------------------+


Special analysis
________________

For analysis which is either difficult to be generalized or is used by the instrument scientists on the
daily-basis, **KaraboFAI** provides special analysis control and plot widgets.