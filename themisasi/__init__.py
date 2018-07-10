#!/usr/bin/env python
"""
Read THEMIS GBO ASI data

to setup spacepy, see  https://scivision.co/installing-spacepy-with-anaconda-python-3

api ref: http://spacepy.lanl.gov/doc/autosummary/spacepy.pycdf.CDF.html
"""
import logging
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


def load(fn: Path,
         treq: Union[str, datetime, List[datetime]]=None,
         calfn: Path=None) -> xarray.Dataset:
    """read THEMIS ASI camera data"""
# %% filename handling
    fn = Path(fn).expanduser()
    if not fn.is_file():
        raise FileNotFoundError(f'video file not found: {fn}')

    fullthumb = fn.name.split('_')[2][-1]
    assert fullthumb in ('t', 'f'), f"unknown file type {fn.name.split('_')[2]}"
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
            time = np.array(list(map(datetime.utcfromtimestamp,
                                     f[f'thg_{key}_{site}_time'][:])))

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
    if len(time) == 0:
        logging.error(f'no times were found with requested time bounds {treq}')
# %% collect output
    imgs = xarray.DataArray(imgs, {'time': time}, ['time', 'y', 'x'],
                            attrs={'filename': fn.name, 'site': site})

    if calfn:
        cal = loadcal(calfn, imgs)
        if cal.site is not None and cal.site != site:
            logging.error(f'cal site {cal.site} and data site {site} do not match. Was wrong calibration file used?')

        data = xarray.merge(({'imgs': imgs}, cal))
        data.attrs = cal.attrs
        data.attrs.update(imgs.attrs)
        if data.caltime is not None:
            if (np.datetime64(data.caltime) >= data.time).any():
                logging.error('calibration is taken AFTER the images--may be incorrect lat/lon az/el plate scale')
    else:
        data = xarray.Dataset({'imgs': imgs})
        data.attrs = imgs.attrs

    return data


def downsample(imgs: xarray.Dataset, az: np.ndarray, el: np.ndarray,
               x: np.ndarray, y: np.ndarray) -> xarray.Dataset:
    """downsamples cal data to match image data
    because of the discontinuous nature of the calibration data, typical resampling is not valid.
    Figured better to add a little error with plain decimation rather than enormous error with invalid technique."""
    if az.shape == imgs.shape[1:]:
        return az, el, x, y

    downscale = (az.shape[0] // imgs.shape[1],
                 az.shape[1] // imgs.shape[2])

    logging.warning(f'downsizing calibration az/el data by factors of {downscale} to match image data')

    az = az[::downscale[0], ::downscale[1]]
    el = el[::downscale[0], ::downscale[1]]
    x = np.arange(az.shape[1])
    y = np.arange(az.shape[0])

    return az, el, x, y


def loadcal(fn: Path, imgs: xarray.Dataset=None) -> xarray.Dataset:
    """
    reads data mapping themis gbo asi pixels to azimuth,elevation
    calibration data url is
    http://data.phys.ucalgary.ca/sort_by_project/THEMIS/asi/skymaps/new_style/
    """
    site = None
    time = None
    fn = Path(fn).expanduser()
    if not fn.is_file():
        raise FileNotFoundError(f'calibration file not found: {fn}')

    if fn.suffix == '.cdf':
        site = fn.name.split('_')[3]
        with pycdf.CDF(str(fn)) as h:
            az = h[f'thg_asf_{site}_azim'][0]
            el = h[f'thg_asf_{site}_elev'][0]
            lat = h[f'thg_asc_{site}_glat'][...]
            lon = (h[f'thg_asc_{site}_glon'][...] + 180) % 360 - 180  # [0,360] -> [-180,180]
            alt_m = h[f'thg_asc_{site}_alti'][...]
            x = y = h[f'thg_asf_{site}_c256'][...]
            time = datetime.utcfromtimestamp(h[f'thg_asf_{site}_time'][-1])
    elif fn.suffix == '.sav':
        site = fn.name.split('_')[2]
        h = readsav(fn, verbose=False)
        az = h['skymap']['full_azimuth'][0]
        el = h['skymap']['full_elevation'][0]
        lat = h['skymap']['site_map_latitude'].item()
        lon = (h['skymap']['site_map_longitude'].item() + 180) % 360 - 180  # [0,360] -> [-180,180]
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
    else:
        raise ValueError(f'{fn} calibration file format is not known to this program.')

    if imgs is not None:
        az, el, x, y = downsample(imgs, az, el, x, y)

    cal = xarray.Dataset({'az': (('y', 'x'), az),
                          'el': (('y', 'x'), el)},
                         coords={'y': y, 'x': x},
                         attrs={'lat': lat, 'lon': lon, 'alt_m': alt_m,
                                'site': site, 'filename': fn.name,
                                'caltime': time})

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
