=================
themis-asi-reader
=================

:Author: Michael Hirsch
:Requirements: Python or Matlab (GNU Octave does not currently have a CDF reader)

A simple function collection to read the 256x256 "high resolution" THEMIS ASI ground-based imager data.



Themis site map (2009)

.. image:: http://themis.ssl.berkeley.edu/data/themis/events/THEMIS_GBO_Station_Map-2009-01.gif
    :alt: Themis site map


Data
====
`Themis all-sky imager data repository <http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/>`_

example
-------

April 14, 2013, 8 UT, play a movie 

::

    wget -P ~/data http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/fykn/2013/04/thg_l1_asf_fykn_2013041408_v01.cdf

Python
~~~~~~
::

    ./readTHEMIS thg_l1_asf_fykn_2013041408_v01.cdf

Matlab
~~~~~~
::

    readTHEMIS('thg_l1_asf_fykn_2013041408_v01.cdf')

