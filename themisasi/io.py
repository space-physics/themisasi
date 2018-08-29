#!/usr/bin/env python
"""
Read THEMIS GBO ASI data
"""
import logging
from pathlib import Path
from datetime import datetime
import xarray
import re
from typing import Tuple, Sequence, Union
import numpy as np
from dateutil.parser import parse
import cdflib
import scipy.io
try:
    import h5py
except ImportError:
    h5py = None
try:
    from netCDF4 import Dataset
except ImportError:
    Dataset = None


Epoch = cdflib.cdfepoch()


def load(fn: Path,
         treq: datetime=None,
         calfn: Path=None) -> xarray.Dataset:
    """read THEMIS ASI camera data"""
# %% filename handling
    fn = Path(fn).expanduser()
    if not fn.is_file():
        raise FileNotFoundError(f'video file not found: {fn}')
# %% time slice (assumes monotonically increasing time)
    imgs = _timeslice(fn, treq)
# %% optional load calibration (az, el)
    data = xarray.Dataset({'imgs': imgs})
    data.attrs = imgs.attrs

    if calfn:
        cal = loadcal(calfn, imgs)
        if cal.site is not None and cal.site != imgs.site:
            raise ValueError(f'cal site {cal.site} and data site {imgs.site} do not match. Was wrong calibration file used?')

        data = xarray.merge((data, cal))
        data.attrs = cal.attrs
        data.attrs.update(imgs.attrs)
        if data.caltime is not None:
            if (np.datetime64(data.caltime) >= data.time).any():
                raise ValueError('calibration is taken AFTER the images--may be incorrect lat/lon az/el plate scale')

    return data


def _timeslice(fn: Path,
               treq: Union[datetime, Sequence[datetime], np.ndarray]=None) -> xarray.DataArray:
    """
    loads time slice of data
    """
# %% open CDF file handle (no close method)
    key, site = _sitekey(fn)

    h = cdflib.CDF(fn)
# %% load image times
    if key.endswith('f'):
        time = Epoch.to_datetime(h[f'thg_{key}_{site}_epoch'][:], to_np=True)
    elif key.endswith('t'):
        time = np.array(list(map(datetime.utcfromtimestamp,
                                 h[f'thg_{key}_{site}_time'][:])))
    else:
        raise ValueError(f"unknown file type {fn.name.split('_')[2]}")
# %% time request handling
    if treq is None:
        pass
    elif isinstance(treq, str):
        treq = parse(treq)
    elif isinstance(treq[0], str):  # type: ignore
        treq = list(map(parse, treq))  # type: ignore
    elif isinstance(treq[0], datetime):  # type: ignore
        pass
    else:
        raise TypeError(f'not sure what treq {treq} is')

    if treq is None:
        i = slice(None)
    else:
        treq = np.atleast_1d(treq)

        if treq.size == 1:
            if (treq < time).all() | (treq > time).all():
                raise ValueError(f'requested time outside {fn}')

            i = abs(time - treq[0]).argmin()
        elif treq.size == 2:  # start, end
            i = (time >= treq[0]) & (time <= treq[1])
        else:
            raise ValueError('for now, time req is single time or time range')

    imgs = h[f'thg_{key}_{site}'][i]
    if imgs.ndim == 2:
        imgs = imgs[None, ...]

    time = time[i]
    if isinstance(time, datetime):
        time = [time]
    elif len(time) == 0:
        raise ValueError(f'no times were found with requested time bounds {treq}')

    return xarray.DataArray(imgs, {'time': time}, ['time', 'y', 'x'],
                            attrs={'filename': fn.name, 'site': site})


def _sitekey(fn: Path) -> Tuple[str, str]:
    """
    gets site name and CDF key from filename (!)
    """
    if not fn.is_file():
        raise FileNotFoundError(f'video file {fn} not found')

    try:
        fullthumb = fn.name.split('_')[2][-1]
    except IndexError:
        raise OSError(f'is {fn} a valid Themis ASI video file?')
# %% info from filename (yuck)
    m = re.search('(?<=thg_l\d_as\w_)\w{4}(?=_.*.cdf)', fn.name)
    if m is None:
        raise OSError(f'filename {fn.name} seems inconsistent with expected Themis ASI naming conventions')

    site = m.group(0)
    key = f'as{fullthumb}'

    return key, site


def _downsample(imgs: xarray.Dataset, az: np.ndarray, el: np.ndarray,
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
        h = cdflib.CDF(fn)
        az = h[f'thg_asf_{site}_azim'][0]
        el = h[f'thg_asf_{site}_elev'][0]
        lat = h[f'thg_asc_{site}_glat']
        lon = (h[f'thg_asc_{site}_glon'] + 180) % 360 - 180  # [0,360] -> [-180,180]
        alt_m = h[f'thg_asc_{site}_alti']
        x = y = h[f'thg_asf_{site}_c256']
        time = datetime.utcfromtimestamp(h[f'thg_asf_{site}_time'][-1])
    elif fn.suffix == '.sav':
        site = fn.name.split('_')[2]
        h = scipy.io.readsav(fn, python_dict=True, verbose=False)
        az = h['skymap']['full_azimuth'][0]
        el = h['skymap']['full_elevation'][0]
        lat = h['skymap']['site_map_latitude'].item()
        lon = (h['skymap']['site_map_longitude'].item() + 180) % 360 - 180  # [0,360] -> [-180,180]
        alt_m = h['skymap']['site_map_altitude'].item()
        x = h['skymap']['full_column'][0][0, :]
        y = h['skymap']['full_row'][0][:, 0]
        tstr = h['skymap']['generation_info'][0][0][2]
        time = datetime(int(tstr[:4]), int(tstr[4:6]), int(tstr[6:8]), int(tstr[8:10]))
    elif fn.suffix == '.h5':
        if h5py is None:
            raise ImportError('pip install h5py')

        with h5py.File(fn, 'r') as h:
            az = h['az'][:]
            el = h['el'][:]
            lat = h['lla'][0]
            lon = h['lla'][1]
            alt_m = h['lla'][2]
            x = h['x'][0, :]
            y = h['y'][:, 0]
    elif fn.suffix == '.nc':
        if Dataset is None:
            raise ImportError('pip install netCDF4')

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
        az, el, x, y = _downsample(imgs, az, el, x, y)

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
