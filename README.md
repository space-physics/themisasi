[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.215309.svg)](https://doi.org/10.5281/zenodo.215309)
[![Travis-CI status](https://travis-ci.org/scivision/themisasi.svg)](https://travis-ci.org/scivision/themisasi)
[![Coverage](https://coveralls.io/repos/github/scivision/themisasi/badge.svg?branch=master)](https://coveralls.io/github/scivision/themisasi?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/d1da43f5a03c6e7456ef/maintainability)](https://codeclimate.com/github/scivision/themisasi/maintainability)
[![pypi versions](https://img.shields.io/pypi/pyversions/themisasi.svg)](https://pypi.python.org/pypi/themisasi)
[![pypi format](https://img.shields.io/pypi/format/themisasi.svg)](https://pypi.python.org/pypi/themisasi)
[![Xarray badge](https://img.shields.io/badge/powered%20by-xarray-orange.svg?style=flat)](http://xarray.pydata.org/en/stable/why-xarray.html)
[![PyPi Download stats](http://pepy.tech/badge/themisasi)](http://pepy.tech/project/themisasi)


# Themis ASI Reader


Read & plot 256x256 "high resolution" THEMIS ASI ground-based imager data.

It also reads the THEMIS ASI star registered 
[plate scale](http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/),
giving **azimuth and elevation** for each pixel.

## Install

Requires
[SpacePy](https://scivision.co/installing-spacepy-with-anaconda-python-3/) 
to read CDF files (not NetCDF).

    python setup_spacepy.py


And as usual:

    python -m pip install -e .

If you have trouble with SpacePy, see 
[SpacePy install notes](https://scivision.co/installing-spacepy-with-anaconda-python-3/).

## Themis site map (2009)

[![Themis site map](http://themis.ssl.berkeley.edu/data/themis/events/THEMIS_GBO_Station_Map-2009-01.gif)](http://themis.ssl.berkeley.edu/gbo/display.py?)

## Reading and Plotting THEMIS ASI Data

Get video data from Themis all-sky imager 
[data repository](http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/)

### April 14, 2013, 8 UT Fort Yukon

    wget -P ~/data http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/fykn/2013/04/thg_l1_asf_fykn_2013041408_v01.cdf

#### Python

    ./PlotThemis thg_l1_asf_fykn_2013041408_v01.cdf

#### Matlab

The Matlab code is obsolete, the Python version has so much more. :

    readTHEMIS('thg_l1_asf_fykn_2013041408_v01.cdf')

## Resources

-   Themis GBO ASI 
    [site coordinates](http://themis.ssl.berkeley.edu/images/ASI/THEMIS_ASI_Station_List_Nov_2011.xls)
-   THEMIS GBO ASI 
    [plate scale](http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/)
-   THEMIS GBO ASI 
    [plate scale](http://themis.ssl.berkeley.edu/themisdata/thg/l2/asi/cal/)
-   Themis GBO ASI 
    [data repository](http://themis.ssl.berkeley.edu/data/themis/thg/l1/asi/)
-   Themis GBO ASI 
    [mosaic (all sites together)](http://themis.ssl.berkeley.edu/gbo/display.py?)

## Themis Plate Scale data

I discovered that IDL 8.0 had a problem saving structured arrays of bytes. 
While current versions of IDL can read these corrupted .sav files, GDL 0.9.4 and SciPy 0.16.1 cannot. 
I submitted a 
[patch to SciPy](https://github.com/scipy/scipy/pull/5801) 
to allow reading these files, which was incorporated into SciPy 0.18.0.

As a fallback, read and rewrite the corrupted file with the IDL script in the 
[idl](idl/) 
directory.
