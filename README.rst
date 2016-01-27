=================
themis-asi-reader
=================

:Author: Michael Hirsch
:Requirements: Python or Matlab (GNU Octave does not currently have a CDF reader)

A simple function collection to read the 256x256 "high resolution" THEMIS ASI ground-based imager data. 
It also reads the `THEMIS ASI star registered plate scale <http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/>`_, giving azimuth and elevation for each pixel.

.. contents::

Install
=======
First, `install SpacePy and CDF <https://scivision.co/installing-spacepy-with-anaconda-python-3/>`_.
Then from Terminal::

    python setup.py develop

Themis site map (2009)
======================

.. image:: http://themis.ssl.berkeley.edu/data/themis/events/THEMIS_GBO_Station_Map-2009-01.gif
    :alt: Themis site map
    :scale: 35%


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
::

    readTHEMIS('thg_l1_asf_fykn_2013041408_v01.cdf')

Themis Plate Scale data
=======================
This involves converting sometimes corrupted IDL .sav files to NetCDF4. The non-corrupted files are convertable by GDL, but some corrupted .sav files will require IDL. The file ``sav2nc.pro`` converts the files with GDL or IDL.

Example Corrupt IDL .sav file needing IDL to convert to NetCDF4
---------------------------------------------------------------
Use IDL with ``sav2nc.pro`` to convert this corrupted file to NetCDF4 so that you can read the data with Python etc.::

    wget http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/fykn_20110305/themis_skymap_fykn_20110305-+_vXX.sav
    
Example IDL .sav file reading with Python
-----------------------------------------
::
    http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/fykn_20081029/themis_skymap_fykn_20061014-20080416_vXX.sav
