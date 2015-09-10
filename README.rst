=================
themis-asi-reader
=================

:Author: Michael Hirsch
:Requirements: Matlab (GNU Octave does not currently have a CDF reader)

A simple function collection to read the 256x256 "high resolution" THEMIS ASI ground-based imager data.

Note: the Matlab code is the only one working at the moment.



Themis site map (2009)

.. image:: http://themis.ssl.berkeley.edu/data/themis/events/THEMIS_GBO_Station_Map-2009-01.gif
    :alt: Themis site map


Data
====
`Themis all-sky imager data repository <http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/>`_

example
-------
April 14, 2013, 8 UT

.. code:: bash

    $ wget -P ~/data http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/fykn/2013/04/thg_l1_asf_fykn_2013041408_v01.cdf

.. code:: matlab

    >> 


Notes
=====
* When I last tried, the `SpacePy/PyCDF library <http://spacepy.lanl.gov/doc/pycdf.html>`_  wasn't quite working for me in Python, but the Matlab code worked fine.
* To use Octave, at the moment one would need to `convert CDF to NetCDF <http://cdf.gsfc.nasa.gov/html/dttools.html>`_ and modify the code to read NetCDF. Probably better to just use Matlab or develop the Python code
