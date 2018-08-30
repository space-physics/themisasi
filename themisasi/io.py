#!/usr/bin/env python
"""
Read THEMIS GBO ASI data
"""
import logging
import warnings
from pathlib import Path
from datetime import datetime, timedelta
import xarray
from typing import Tuple, Sequence, Union, Optional
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
cdfread = cdflib.cdfread.CDF


def load(path: Path,
         site: str=None,
         treq: datetime=None,
         calfn: Path=None) -> xarray.Dataset:
    """read THEMIS ASI camera data"""
# %% time slice (assumes monotonically increasing time)
    treq = _timereq(treq)

    imgs = _timeslice(path, site, treq)
# %% optional load calibration (az, el)
    data = xarray.Dataset({'imgs': imgs})
    data.attrs = imgs.attrs

    cal = None
    if calfn:
        cal = loadcal(calfn)
    else:
        try:
            cal = loadcal(path, site, treq)
        except FileNotFoundError:
            pass

    if cal is not None:
        if cal.site is not None and cal.site != imgs.site:
            raise ValueError(f'cal site {cal.site} and data site {imgs.site} do not match. Was wrong calibration file used?')

        data = xarray.merge((data, cal))
        data.attrs = cal.attrs
        data.attrs.update(imgs.attrs)
        if data.caltime is not None:
            if (np.datetime64(data.caltime) >= data.time).any():
                raise ValueError('calibration is taken AFTER the images--may be incorrect lat/lon az/el plate scale')

    return data


def _timeslice(path: Path, site: str=None,
               treq: Union[datetime, Sequence[datetime], np.ndarray]=None) -> xarray.DataArray:
    """
    loads time slice of data
    """
# %% open CDF file handle (no close method)
    site, fn = _sitefn(path, site, treq)

    h = cdfread(fn)
# %% load image times
    try:
        time = Epoch.to_datetime(h[f'thg_asf_{site}_epoch'][:], to_np=True)
    except KeyError:
        time = np.array(list(map(datetime.utcfromtimestamp,
                                 h[f'thg_asf_{site}_time'][:])))
# %% time request handling
    if treq is None:
        i = slice(None)
    else:
        treq = np.atleast_1d(treq)

        if treq.size == 1:
            # Note: arbitrarily allowing up to 1 second time offset from request
            if (treq < time-timedelta(seconds=1)).all() | (treq > time+timedelta(seconds=1)).all():
                raise ValueError(f'requested time outside {fn}')

            i = abs(time - treq[0]).argmin()
        elif treq.size == 2:  # start, end
            i = (time >= treq[0]) & (time <= treq[1])
        else:
            raise ValueError('for now, time req is single time or time range')

    imgs = h[f'thg_asf_{site}'][i]
    if imgs.ndim == 2:
        imgs = imgs[None, ...]

    time = time[i]
    if isinstance(time, datetime):
        time = [time]
    elif len(time) == 0:
        raise ValueError(f'no times were found with requested time bounds {treq}')

    return xarray.DataArray(imgs, {'time': time}, ['time', 'y', 'x'],
                            attrs={'filename': fn.name, 'site': site})


def _sitefn(path: Path, site: str=None,
            treq: Union[datetime, Sequence[datetime], np.ndarray]=None) -> Tuple[str, Path]:
    """
    gets site name and CDF key from filename (!)
    """

    path = Path(path).expanduser()

    if path.is_dir():
        if not isinstance(site, str):
            raise ValueError('Must specify filename OR path and site and time')

        if len(site) != 4:
            raise ValueError(f'site name is four character lower-case e.g. fykn. You gave:  {site}')
        # FIXME: assumes time bounds don't cross file boundaries
        if treq is None:
            raise ValueError('Must specify filename OR path and site and time')
        elif isinstance(treq, datetime):
            t0 = treq
        elif isinstance(treq[0], datetime) and len(treq) in (1, 2):
            t0 = treq[0]
        else:
            raise ValueError('Must specify filename OR path and site and time')

        fn = path / f'thg_l1_asf_{site}_{t0.year}{t0.month:02d}{t0.day:02d}{t0.hour:02d}_v01.cdf'
        if not fn.is_file():
            # try to use last time in file, if first time wasn't covered
            if isinstance(treq, datetime):
                raise FileNotFoundError(fn)

            t0 = treq[-1]

            fn = path / f'thg_l1_asf_{site}_{t0.year}{t0.month:02d}{t0.day:02d}{t0.hour:02d}_v01.cdf'

    elif path.is_file():
        if site:
            raise ValueError('specify filename OR site')

        fn = path

        h = cdfread(fn)
        site = h.attget('Descriptor', 0)['Data'][:4].lower()
    else:
        raise FileNotFoundError(f'video file not found in {path}')

    assert isinstance(site, str)

    return site, fn


def _timereq(treq: datetime=None) -> Optional[datetime]:

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

    return treq


def _downsample(imgs: xarray.Dataset, az: np.ndarray, el: np.ndarray,
                x: np.ndarray, y: np.ndarray) -> xarray.Dataset:
    """downsamples cal data to match image data
    because of the discontinuous nature of the calibration data, typical resampling is not valid.
    Figured better to add a little error with plain decimation rather than enormous error with invalid technique.
    """
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


def loadcal_file(fn: Path) -> xarray.Dataset:
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
        h = cdfread(fn)
        az = h[f'thg_asf_{site}_azim'][0]
        el = h[f'thg_asf_{site}_elev'][0]
        lat = h[f'thg_asc_{site}_glat']
        lon = (h[f'thg_asc_{site}_glon'] + 180) % 360 - 180  # [0,360] -> [-180,180]
        alt_m = h[f'thg_asc_{site}_alti']
        x = y = h[f'thg_asf_{site}_c256']
        time = datetime.utcfromtimestamp(h[f'thg_asf_{site}_time'][-1])
    elif fn.suffix == '.sav':
        site = fn.name.split('_')[2]
        # THEMIS SAV calibration files written with glitch from bug in IDL
        warnings.simplefilter("ignore", UserWarning)
        h = scipy.io.readsav(fn, python_dict=True, verbose=False)
        warnings.resetwarnings()

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

    cal = xarray.Dataset({'az': (('y', 'x'), az),
                          'el': (('y', 'x'), el)},
                         coords={'y': y, 'x': x},
                         attrs={'lat': lat, 'lon': lon, 'alt_m': alt_m,
                                'site': site, 'filename': fn.name,
                                'caltime': time})

    return cal


def loadcal(path: Path, site: str=None, time: datetime=None) -> xarray.Dataset:
    path = Path(path).expanduser()

    if path.is_file() and site is None or time is None:
        try:
            return loadcal_file(path)
        except KeyError:
            return None
    elif path.is_file():
        path = path.parent

    assert isinstance(site, str)
    fn = _findcal(path, site, time)

    return loadcal_file(fn)


def _findcal(path: Path, site: str, time: datetime) -> Path:
    """
    attempt to find nearest previous time calibration file
    """

    if not path.is_dir():
        raise FileNotFoundError(str(path))

    if not isinstance(site, str) or len(site) != 4:
        raise ValueError(f'site code is four characters e.g. fykn.  You gave:   {site}')

    if isinstance(time, str):
        time = parse(time)

    if isinstance(time, (list, tuple, np.ndarray)):
        time = time[0]  # assume first time is earliest

    if not isinstance(time, datetime):
        raise TypeError(f'must specify single datetime, you gave:  {time}')
# %% CDF .cdf
    fcdf = sorted(path.glob(f'thg_l2_asc_{site}_*.cdf'))
    dates = [loadcal(fn).caltime for fn in fcdf]

    datecdf = None
    if dates:
        for i, date in enumerate(dates[::-1]):
            if date < time:
                break
        if date < time:
            datecdf = date
            icdf = len(fcdf) - (i+1)
# %% IDL .sav
    fsav = sorted(path.glob(f'themis_skymap_{site}_*.sav'))
    dates = [loadcal(fn).caltime for fn in fsav]

    datesav = None
    if dates:
        for i, date in enumerate(dates[::-1]):
            if date < time:
                break
        if date < time:
            datesav = date
            isav = len(fsav) - (i+1)

# %% get result
    if not dates:
        raise FileNotFoundError(f'could not find cal file for {site} {time}  in {path}')
    elif datecdf is None:
        return fsav[isav]
    elif datesav is None:
        return fcdf[icdf]
# tiebreaker
    diff = [abs(datecdf-time), abs(datesav-time)]
    idff = diff.index(min(diff))

    if idff == 0:
        return fcdf[icdf]
    else:
        return fsav[isav]
