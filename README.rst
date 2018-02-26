.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.215309.svg
   :target: https://doi.org/10.5281/zenodo.215309

.. image:: https://travis-ci.org/scivision/themisasi.svg
    :target: https://travis-ci.org/scivision/themisasi

.. image:: https://coveralls.io/repos/github/scivision/themisasi/badge.svg?branch=master
    :target: https://coveralls.io/github/scivision/themisasi?branch=master

.. image:: https://api.codeclimate.com/v1/badges/d1da43f5a03c6e7456ef/maintainability
   :target: https://codeclimate.com/github/scivision/themisasi/maintainability
   :alt: Maintainability


=================
themis-asi-reader
=================

:Author: Michael Hirsch
:Prereq: `SpacePy <https://scivision.co/installing-spacepy-with-anaconda-python-3/>`_

Read & plot 256x256 "high resolution" THEMIS ASI ground-based imager data.

It also reads the `THEMIS ASI star registered plate scale <http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/>`_, giving **azimuth and elevation** for each pixel.

.. contents::

Install
=======
::

    python -m pip install -e .


If you have trouble with SpacePy, see `SpacePy install notes <https://scivision.co/installing-spacepy-with-anaconda-python-3/>`_.

Themis site map (2009)
======================

.. image:: http://themis.ssl.berkeley.edu/data/themis/events/THEMIS_GBO_Station_Map-2009-01.gif
    :alt: Themis site map
    :scale: 35%
    :target: http://themis.ssl.berkeley.edu/gbo/display.py?


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
`Themis GBO ASI site coordinates <http://themis.ssl.berkeley.edu/images/ASI/THEMIS_ASI_Station_List_Nov_2011.xls>`_

`THEMIS GBO ASI plate scale <http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/>`_

`Themis GBO ASI data repository <http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/>`_

`Themis GBO ASI mosaic (all sites together) <http://themis.ssl.berkeley.edu/gbo/display.py?>`_


Themis Plate Scale data
=======================
I discovered that IDL 8.0 had a problem saving structured arrays of bytes.
While current versions of IDL can read these corrupted .sav files, GDL 0.9.4 and SciPy 0.16.1 cannot.
I submitted a `patch to SciPy <https://github.com/scipy/scipy/pull/5801>`_ to allow reading these files. If you get an error, try making the patch yourself.

As a fallback, read and rewrite the corrupted file with the IDL script in the `idl <idl/>`_ directory.

