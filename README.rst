.. image:: https://travis-ci.org/scienceopen/themisasi.svg?branch=master
    :target: https://travis-ci.org/scienceopen/themisasi

=================
themis-asi-reader
=================

:Author: Michael Hirsch
:Requirements: Python, SpacePy and `CDF <https://scivision.co/installing-spacepy-with-anaconda-python-3/>`_

A simple function collection to read the 256x256 "high resolution" THEMIS ASI ground-based imager data. 
It also reads the `THEMIS ASI star registered plate scale <http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/>`_, giving azimuth and elevation for each pixel.

.. contents::

Install
=======
First `install SpacePy and CDF <https://scivision.co/installing-spacepy-with-anaconda-python-3/>`_
::

    python setup.py develop

Themis site map (2009)
======================

.. image:: http://themis.ssl.berkeley.edu/data/themis/events/THEMIS_GBO_Station_Map-2009-01.gif
    :alt: Themis site map
    :scale: 35%
    :target: http://themis.ssl.berkeley.edu/asi_map.shtml


Reading and Plotting THEMIS ASI Data
====================================
Get video data from `Themis all-sky imager data repository <http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/>`_

April 14, 2013, 8 UT Fort Yukon
-------------------------------
::

    wget -P ~/data http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/fykn/2013/04/thg_l1_asf_fykn_2013041408_v01.cdf

Python
~~~~~~
::

    ./PlotThemis thg_l1_asf_fykn_2013041408_v01.cdf

Matlab
~~~~~~
The Matlab code is obsolete, the Python version has so much more.
::

    readTHEMIS('thg_l1_asf_fykn_2013041408_v01.cdf')

Resources
=========
`Themis ASI coordinate spreadsheet <http://themis.ssl.berkeley.edu/images/ASI/THEMIS_ASI_Station_List_Nov_2011.xls>`_

`THEMIS ASI star registered plate scale <http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/>`_

`Themis all-sky imager data repository <http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/>`_


Themis Plate Scale data
=======================
I discovered that IDL 8.0 had a problem saving structured arrays of bytes. While current versions of IDL can read these corrupted .sav files, GDL 0.9.4 and SciPy 0.16.1 cannot. `I submitted a patch to SciPy to allow reading these files. If you get an error, try making the patch yourself. <https://github.com/scipy/scipy/pull/5801>`_

