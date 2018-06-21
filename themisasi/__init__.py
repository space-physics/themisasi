#!/usr/bin/env python
"""
Read THEMIS GBO ASI data

to setup spacepy, see  https://scivision.co/installing-spacepy-with-anaconda-python-3

api ref: http://spacepy.lanl.gov/doc/autosummary/spacepy.pycdf.CDF.html
"""
from pathlib import Path
from datetime import datetime
import xarray
import re
import numpy as np
from dateutil.parser import parse
from spacepy import pycdf
import h5py
from scipy.io import readsav
from typing import List, Union
from netCDF4 import Dataset
#


def load(fn: Path,
         treq: Union[str, datetime, List[datetime]]=None,
         calfn: Path=None, fullthumb: str='f') -> xarray.Dataset:
    """read THEMIS ASI camera data"""
    assert fullthumb in ('t', 'f')

    fn = Path(fn).expanduser()
# %% info from filename (yuck)
    m = re.search('(?<=thg_l\d_as\w_)\w{4}(?=_.*.cdf)', fn.name)
    if m is None:
        raise OSError(f'filename {fn.name} seems inconsistent with expected Themis ASI naming conventions')

    site = m.group(0)
    key = f'as{fullthumb}'

    if treq is None:
        pass
    elif isinstance(treq, str):
        treq = parse(treq)
    elif isinstance(treq, (tuple, list)) and isinstance(treq[0], str):
        treq = list(map(parse, treq))
    elif isinstance(treq, (tuple, list)) and isinstance(treq[0], datetime):
        pass
    else:
        raise TypeError(f'not sure what treq {treq} is')
# %% time slice (assumes monotonically increasing time)
    with pycdf.CDF(str(fn)) as f:
        if fullthumb == 'f':
            time = f[f'thg_{key}_{site}_epoch'][:]
        elif fullthumb == 't':
            time = list(map(datetime.utcfromtimestamp,
                            f[f'thg_{key}_{site}_time'][:]))

        if treq is None:
            i = slice(None)
        elif isinstance(treq, datetime):
            i = slice(abs(time - treq).argmin())
        elif len(treq) == 2:  # start, end
            i = slice(abs(time - treq[0]).argmin(), abs(time - treq[1]).argmin())
        else:
            raise ValueError('for now, time req is single time or time range')

        imgs = f[f'thg_{key}_{site}'][i]

    time = time[i]
# %% collect output
    imgs = xarray.DataArray(imgs, {'time': time}, ['time', 'y', 'x'],
                            attrs={'filename': fn, 'site': site})

    if calfn:
        cal = loadcal(calfn)
        data = xarray.merge(({'imgs': imgs}, cal))
        data.attrs = cal.attrs
        data.attrs.update(imgs.attrs)
    else:
        data = xarray.Dataset({'imgs': imgs})
        data.attrs = imgs.attrs

    return data


def loadcal(fn: Path) -> xarray.Dataset:
    """
    reads data mapping themis gbo asi pixels to azimuth,elevation
    calibration data url is
    http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/
    """
    site = None
    fn = Path(fn).expanduser()
    if fn.suffix == '.sav':
        site = fn.name.split('_')[2]
        h = readsav(fn, verbose=False)
        az = h['skymap']['full_azimuth'][0]
        el = h['skymap']['full_elevation'][0]
        lat = h['skymap']['site_map_latitude'].item()
        lon = (h['skymap']['site_map_longitude'].item() +
               180) % 360 - 180  # [0,360] -> [-180,180]
        alt_m = h['skymap']['site_map_altitude'].item()
        x = h['skymap']['full_column'][0][0, :]
        y = h['skymap']['full_row'][0][:, 0]
    elif fn.suffix == '.h5':
        with h5py.File(fn, 'r') as h:
            az = h['az'][:]
            el = h['el'][:]
            lat = h['lla'][0]
            lon = h['lla'][1]
            alt_m = h['lla'][2]
            x = h['x'][0, :]
            y = h['y'][:, 0]
    elif fn.suffix == '.nc':
        with Dataset(fn, 'r') as h:
            az = h['az'][:]
            el = h['el'][:]
            lat = h['lla'][0]
            lon = h['lla'][1]
            alt_m = h['lla'][2]
            x = h['x'][0, :].astype(int)
            y = np.flipud(h['y'][:, 0]).astype(int)

    cal = xarray.Dataset({'az': (('y', 'x'), az),
                          'el': (('y', 'x'), el)},
                         coords={'y': y, 'x': x},
                         attrs={'lat': lat, 'lon': lon, 'alt_m': alt_m,
                                'site': site, 'filename': fn.name})

    return cal

# def calmulti(flist):
#    """
#    read plate scale data of other cameras and store in lists for iteration
#    use lists because other cameras might each have unique pixel counts or configurations
#    """
#    if isinstance(flist,str): flist = [flist]
#    flist = [Path(f).expanduser() for f in flist]
#
#    az = []; el = [] #each image might be a different size
#    lla = empty((len(flist),3))
#    for i,f in enumerate(flist):
#        a,e,l,x,y = calread(f)
#        az.append(a); el.append(e); lla[i,:] = l
#
#    return az,el,lla
